# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import config
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import pandas as pd
import glob
import random
from data_processing_tracker import update_file_metadata



namespace_cache = {}  # Cache for storing namespaces

def extract_namespace(xml_file_path):
    for _, elem in ET.iterparse(xml_file_path, events=("start",)):
        # Get the namespace from the first element
        namespace = elem.tag.split('}')[0].strip('{')
        return namespace

def get_namespace(area_code, xml_file_path):
    if area_code not in namespace_cache:
        namespace_uri = extract_namespace(xml_file_path)
        namespace_cache[area_code] = {'ns': namespace_uri}  # Store as a dictionary
    return namespace_cache[area_code]


def parse_xml_to_df(xml_file_path):
    """
    Parse the XML file containing electricity price data and convert it to a pandas DataFrame.

    Parameters:
    xml_file_path (str): The path to the XML file containing the data.

    Returns:
    DataFrame: The converted data as a pandas DataFrame.
    """

    # Extract area code from the filename
    area_code = os.path.basename(xml_file_path).split('_')[0]

    # Retrieve or extract the namespace using the area code
    ns = get_namespace(area_code, xml_file_path)  # ns is now a dictionary

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

def process_files(file_list):
    for xml_file in file_list:
        df = parse_xml_to_df(xml_file)
        # Replace '.xml' with '_preprocessed.csv' to get the new filename
        csv_filename = os.path.basename(xml_file).replace('.xml', '_preprocessed.csv')
        # Join with the directory path
        csv_file_path = os.path.join(config.DATA_PROCESSED_DIR, csv_filename)
        # Save DataFrame to CSV
        save_df_to_csv(df, csv_filename, directory=config.DATA_PROCESSED_DIR)
        # Update the file metadata using the full path
        update_file_metadata(csv_file_path, 'preprocessed')

def process_all_xml_files():
    xml_files = glob.glob(os.path.join(config.DATA_RAW_DIR, '*.xml'))
    process_files(xml_files)

def process_first_x_files(x):
    xml_files = sorted(glob.glob(os.path.join(config.DATA_RAW_DIR, '*.xml')))[:x]
    process_files(xml_files)

def process_last_x_files(x):
    xml_files = sorted(glob.glob(os.path.join(config.DATA_RAW_DIR, '*.xml')))[-x:]
    process_files(xml_files)

def process_random_x_files(x):
    xml_files = glob.glob(os.path.join(config.DATA_RAW_DIR, '*.xml'))
    if len(xml_files) < x:
        selected_files = xml_files
    else:
        selected_files = random.sample(xml_files, x)
    process_files(selected_files)



if __name__ == "__main__":
    
    # Example usage for specific files
    # xml_file_path = 'NO1_Week40_2023_10_02_to_2023_10_08_prices.xml'  # Replace with your XML file path
    
    user_choice = input("Choose an option: 'specific', 'all', 'first X', 'last X', or 'random X' files: ").strip().lower()

    if user_choice == 'specific':
        file_name = input("Enter the name of the file to process (e.g., 'example.xml'): ").strip()
        xml_file_path = os.path.join(config.DATA_RAW_DIR, file_name)

        if os.path.exists(xml_file_path):
            processed_data_df = parse_xml_to_df(xml_file_path)
            csv_filename = file_name.replace('.xml', '.csv')
            save_df_to_csv(processed_data_df, csv_filename)
            print(f"Processed file saved as: {csv_filename}")
        else:
            print(f"File not found: {xml_file_path}")

    elif user_choice == 'all':
        process_all_xml_files()
        print("Processed all files in the raw data directory.")

    elif user_choice.startswith('first') or user_choice.startswith('last'):
        try:
            num_files = int(user_choice.split()[1])
            if num_files < 0:
                raise ValueError("Number of files must be non-negative.")
            
            if user_choice.startswith('first'):
                process_first_x_files(num_files)
                print(f"Processed the first {num_files} files in the raw data directory.")
            else:
                process_last_x_files(num_files)
                print(f"Processed the last {num_files} files in the raw data directory.")
                
        except (IndexError, ValueError) as e:
            print(f"Invalid input: {e}")
    
    elif user_choice.startswith('random'):
        try:
            num_files = int(user_choice.split()[1])
            if num_files < 0:
                raise ValueError("Number of files must be non-negative.")
            process_random_x_files(num_files)
            print(f"Processed a random selection of {num_files} files from the raw data directory.")
        except (IndexError, ValueError) as e:
            print(f"Invalid input: {e}")

    else:
        print("Invalid input. Please enter one of the specified options.")