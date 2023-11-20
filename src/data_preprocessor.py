# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import pandas as pd

def parse_xml_to_df(xml_file_path):
    """
    Parse the XML file containing electricity price data and convert it to a pandas DataFrame.

    Parameters:
    xml_file_path (str): The path to the XML file containing the data.

    Returns:
    DataFrame: The converted data as a pandas DataFrame.
    """
    # Define the namespace map to use with the XML
    ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0'}  # Namespace

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data_records = []
    for timeseries in root.findall('.//ns:TimeSeries', ns):
        business_type = timeseries.find('ns:businessType', ns).text
        in_domain = timeseries.find('ns:in_Domain.mRID', ns).text
        out_domain = timeseries.find('ns:out_Domain.mRID', ns).text
        currency = timeseries.find('ns:currency_Unit.name', ns).text

        for period in timeseries.findall('.//ns:Period', ns):
            start_of_period = datetime.fromisoformat(period.find('.//ns:timeInterval/ns:start', ns).text)

            for point in period.findall('.//ns:Point', ns):
                position = int(point.find('ns:position', ns).text)
                price_amount = float(point.find('ns:price.amount', ns).text)

                # Adjust period_start and period_end based on the position
                hour_adjustment = timedelta(hours=position - 1)
                period_start = start_of_period + hour_adjustment
                period_end = period_start + timedelta(hours=1)

                data_records.append({
                    'price': price_amount,
                    'business_type': business_type,
                    'in_domain': in_domain,
                    'out_domain': out_domain,
                    'currency': currency,
                    'period_start': period_start.isoformat(),
                    'period_end': period_end.isoformat()
                })

    df = pd.DataFrame(data_records)
    return df

def save_df_to_csv(df, filename, directory='data/processed'):
    """
    Save a DataFrame to a CSV file in the specified directory.

    Parameters:
    df (DataFrame): The pandas DataFrame to save.
    filename (str): The filename to use, without the directory path.
    directory (str): The directory where the file will be saved.
    """

    # Define the full file path
    file_path = os.path.join(directory, filename)
    
    # Save the DataFrame to CSV
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    
    # Example usage
    xml_file_path = 'data/raw/10Y1001A1001A48H_20231102_to_20231103_prices.xml'  # Replace with your XML file path
    
    # Check if the file exists
    if os.path.exists(xml_file_path):
        processed_data_df = parse_xml_to_df(xml_file_path)
        save_df_to_csv(processed_data_df, 'processed_data.csv')
    else:
        print(f"File not found: {xml_file_path}")