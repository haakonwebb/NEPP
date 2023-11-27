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
from utils import save_df_to_csv

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

def check_area_code_folder(area_code):
    """
    Check if the folder for the given area code exists.

    Parameters:
    area_code (str): The area code.

    Returns:
    bool: True if the folder exists, False otherwise.
    """
    folder_path = os.path.join(config.DATA_RAW_DIR, area_code)
    return os.path.exists(folder_path)

def parse_xml_to_df(xml_file_path, user_start_date, user_end_date):
    """
    Parse the XML file containing electricity price data and convert it to a pandas DataFrame.

    Parameters:
    xml_file_path (str): The path to the XML file containing the data.
    start_date (str): The start date in 'YYYY-MM-DD' format.
    end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
    DataFrame: The converted data as a pandas DataFrame.
    """

    area_code = os.path.basename(xml_file_path).split('_')[0]
    ns = get_namespace(area_code, xml_file_path)

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data_records = []

    # Remember to change the timezones if necessary
    start_date = pd.Timestamp(user_start_date).tz_localize('UTC')
    end_date = pd.Timestamp(user_end_date).tz_localize('UTC') + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # Include last measurement of end_date

    for timeseries in root.findall('.//ns:TimeSeries', ns):
        business_type = timeseries.find('ns:businessType', ns).text
        in_domain = timeseries.find('ns:in_Domain.mRID', ns).text
        out_domain = timeseries.find('ns:out_Domain.mRID', ns).text
        currency = timeseries.find('ns:currency_Unit.name', ns).text

        for period in timeseries.findall('.//ns:Period', ns):
            period_start = datetime.fromisoformat(period.find('.//ns:timeInterval/ns:start', ns).text)
            period_end = datetime.fromisoformat(period.find('.//ns:timeInterval/ns:end', ns).text)
            
            for point in period.findall('.//ns:Point', ns):
                position = int(point.find('ns:position', ns).text)
                price_amount = float(point.find('ns:price.amount', ns).text)

                hour_adjustment = timedelta(hours=position - 1)
                measurement_start_time = pd.Timestamp(period_start + hour_adjustment).tz_convert('UTC')

                # Ensure 'measurement_start_time' is within the period range
                if not (period_start <= measurement_start_time < period_end):
                    continue

                # Skip data points outside the specified date range
                if measurement_start_time < start_date or measurement_start_time > end_date:
                    continue

                data_records.append({
                    'price': price_amount,
                    'business_type': business_type,
                    'in_domain': in_domain,
                    'out_domain': out_domain,
                    'currency': currency,
                    'period_start': measurement_start_time.isoformat(),
                    'period_end': (measurement_start_time + timedelta(hours=1)).isoformat()
                })

    df = pd.DataFrame(data_records)

    # Ensure 'period_start' is in datetime format
    df['period_start'] = pd.to_datetime(df['period_start'])

    return df

def process_files(file_list, user_start_date, user_end_date):
    for xml_file in file_list:
        df = parse_xml_to_df(xml_file, user_start_date, user_end_date)

        # Group by year and save each group in a separate file
        for year, year_df in df.groupby(df['period_start'].dt.year):
            area_code = os.path.basename(xml_file).split('_')[0]
            area_code_folder = os.path.join(config.DATA_PREPROCESSED_DIR, area_code)
            os.makedirs(area_code_folder, exist_ok=True)

            # File naming based on area code and year
            file_name = f"{area_code}_{year}.csv"
            preprocessed_file_path = os.path.join(area_code_folder, file_name)

            # Check if the file already exists to determine append or create a new one
            if os.path.exists(preprocessed_file_path):
                # Append without header
                year_df.to_csv(preprocessed_file_path, mode='a', index=False, header=False)
            else:
                # Create a new file with header
                year_df.to_csv(preprocessed_file_path, index=False)

            try:
                update_file_metadata(preprocessed_file_path, 'preprocessed')
                print(f"Metadata updated for {preprocessed_file_path}")
            except Exception as e:
                print(f"Error updating metadata for {preprocessed_file_path}: {e}")

def process_all_xml_files(area_code, user_start_date, user_end_date):
    folder_path = os.path.join(config.DATA_RAW_DIR, area_code)
    xml_files = glob.glob(os.path.join(folder_path, '*.xml'))
    process_files(xml_files, user_start_date, user_end_date)

def process_first_x_files(area_code, x, user_start_date, user_end_date):
    folder_path = os.path.join(config.DATA_RAW_DIR, area_code)
    xml_files = sorted(glob.glob(os.path.join(folder_path, '*.xml')))[:x]
    process_files(xml_files, user_start_date, user_end_date)

def process_last_x_files(area_code, x, user_start_date, user_end_date):
    folder_path = os.path.join(config.DATA_RAW_DIR, area_code)
    xml_files = sorted(glob.glob(os.path.join(folder_path, '*.xml')))[-x:]
    process_files(xml_files, user_start_date, user_end_date)

def process_random_x_files(area_code, x, user_start_date, user_end_date):
    folder_path = os.path.join(config.DATA_RAW_DIR, area_code)
    xml_files = glob.glob(os.path.join(folder_path, '*.xml'))
    
    if len(xml_files) < x:
        selected_files = xml_files
    else:
        selected_files = random.sample(xml_files, x)

    process_files(selected_files, user_start_date, user_end_date)

if __name__ == "__main__":
    
    # Example usage for specific files
    # xml_file_path = 'NO1_Week40_2023_10_02_to_2023_10_08_day_ahead_prices.xml'  # Replace with your XML file path
    
    area_code = input("Enter the area code (e.g., 'NO1'): ").strip().upper()
    
    if not check_area_code_folder(area_code):
        print(f"No data folder found for area code {area_code}. Exiting.")
        exit()

    user_start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
    user_end_date = input("Enter the end date (YYYY-MM-DD): ").strip()

    user_choice = input("Choose an option: 'specific', 'all', 'first X', 'last X', or 'random X' files: ").strip().lower()

    if user_choice == 'specific':
        file_name = input("Enter the name of the file to process (e.g., 'example.xml'): ").strip()
        xml_file_path = os.path.join(config.DATA_RAW_DIR, area_code, file_name)

        if os.path.exists(xml_file_path):
            processed_data_df = parse_xml_to_df(xml_file_path, user_start_date, user_end_date)
            csv_filename = file_name.replace('.xml', '.csv')
            save_df_to_csv(processed_data_df, csv_filename)
            print(f"Processed file saved as: {csv_filename}")
        else:
            print(f"File not found: {xml_file_path}")

    elif user_choice == 'all':
        process_all_xml_files(area_code, user_start_date, user_end_date)
        print("Processed all files in the specified area code directory.")

    elif user_choice.startswith('first'):
        num_files = int(user_choice.split()[1])
        process_first_x_files(area_code, num_files, user_start_date, user_end_date)
        print(f"Processed the first {num_files} files in the specified area code directory.")

    elif user_choice.startswith('last'):
        num_files = int(user_choice.split()[1])
        process_last_x_files(area_code, num_files, user_start_date, user_end_date)
        print(f"Processed the last {num_files} files in the specified area code directory.")

    elif user_choice.startswith('random'):
        num_files = int(user_choice.split()[1])
        process_random_x_files(area_code, num_files, user_start_date, user_end_date)
        print(f"Processed a random selection of {num_files} files from the specified area code directory.")

    else:
        print("Invalid input. Please enter one of the specified options.")