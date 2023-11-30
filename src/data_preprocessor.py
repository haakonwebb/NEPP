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
import pytz

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

def parse_xml_to_df(xml_file_path):
    """
    Parse the XML file containing electricity price data and convert it to a pandas DataFrame.

    Parameters:
    xml_file_path (str): The path to the XML file containing the data.

    Returns:
    DataFrame: The converted data as a pandas DataFrame.
    """

    area_code = os.path.basename(xml_file_path).split('_')[0]
    # Assuming get_namespace is a function defined elsewhere in your code
    ns = get_namespace(area_code, xml_file_path)

    # Extracting start and end dates from the file name
    file_name_parts = os.path.basename(xml_file_path).split('_')
    file_start_date = ''.join(file_name_parts[1:4])  # Joins year, month, day
    file_end_date = ''.join(file_name_parts[5:8])   # Joins year, month, day

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data_records = []
    
    # Define UTC and UTC+1 timezones
    utc_plus_1 = pytz.FixedOffset(60)  # 60 minutes offset for UTC+1

    # Convert input dates to offset-aware UTC+1
    start_date = datetime.strptime(file_start_date, '%Y%m%d')
    end_date = datetime.strptime(file_end_date, '%Y%m%d') + timedelta(days=1) - timedelta(seconds=1)

    start_date_utc1 = utc_plus_1.localize(start_date)
    end_date_utc1 = utc_plus_1.localize(end_date)

    for timeseries in root.findall('.//ns:TimeSeries', ns):
        business_type = timeseries.find('ns:businessType', ns).text
        in_domain = timeseries.find('ns:in_Domain.mRID', ns).text
        out_domain = timeseries.find('ns:out_Domain.mRID', ns).text
        currency = timeseries.find('ns:currency_Unit.name', ns).text

        for period in timeseries.findall('.//ns:Period', ns):
            period_start_str = period.find('.//ns:timeInterval/ns:start', ns).text
            
            # Convert the string to a datetime object
            period_start = datetime.fromisoformat(period_start_str)

            # Localize to UTC if tzinfo is None
            if period_start.tzinfo is None:
                period_start = pytz.utc.localize(period_start)

            for point in period.findall('.//ns:Point', ns):
                position = int(point.find('ns:position', ns).text)
                price_amount = float(point.find('ns:price.amount', ns).text)

                hour_adjustment = timedelta(hours=position - 1)

                # Convert the measurement start time to UTC+1
                measurement_start_time_utc1 = period_start + hour_adjustment
                measurement_start_time_utc1 = measurement_start_time_utc1.astimezone(pytz.FixedOffset(60))

                # Check if measurement_start_time is within the specified date range
                if not (measurement_start_time_utc1 >= start_date_utc1 and measurement_start_time_utc1 <= end_date_utc1):
                    continue

                data_records.append({
                    'price': price_amount,
                    'business_type': business_type,
                    'in_domain': in_domain,
                    'out_domain': out_domain,
                    'currency': currency,
                    'period_start': measurement_start_time_utc1.isoformat(),
                    'period_end': (measurement_start_time_utc1 + timedelta(hours=1)).isoformat()
                })

    df = pd.DataFrame(data_records)

    # Only convert if 'period_start' column exists
    if 'period_start' in df.columns:
        df['period_start'] = pd.to_datetime(df['period_start'])
        df['period_end'] = pd.to_datetime(df['period_end'])

    return df

def process_files(file_list):
    for xml_file in file_list:
        df = parse_xml_to_df(xml_file)

        for year, year_df in df.groupby(df['period_start'].dt.year):
            area_code = os.path.basename(xml_file).split('_')[0]
            area_code_folder = os.path.join(config.DATA_PREPROCESSED_DIR, area_code)
            os.makedirs(area_code_folder, exist_ok=True)

            file_name = f"{area_code}_{year}.csv"
            preprocessed_file_path = os.path.join(area_code_folder, file_name)

            if os.path.exists(preprocessed_file_path):
                existing_df = pd.read_csv(preprocessed_file_path)

                # Convert 'period_start' to datetime for both DataFrames
                existing_df['period_start'] = pd.to_datetime(existing_df['period_start'])
                year_df['period_start'] = pd.to_datetime(year_df['period_start'])

                # Combine the data
                combined_df = pd.concat([existing_df, year_df])

                # Drop duplicates and sort the data in descending order
                combined_df.drop_duplicates(subset=['period_start'], inplace=True)
                combined_df.sort_values(by='period_start', inplace=True)

                combined_df.to_csv(preprocessed_file_path, index=False)
            else:
                year_df.to_csv(preprocessed_file_path, index=False)

            try:
                update_file_metadata(preprocessed_file_path, 'preprocessed')
                print(f"Metadata updated for {preprocessed_file_path}")
            except Exception as e:
                print(f"Error updating metadata for {preprocessed_file_path}: {e}")

def filter_xml_files_by_year(area_code, start_year, end_year):
    folder_path = os.path.join(config.DATA_RAW_DIR, area_code)
    all_xml_files = glob.glob(os.path.join(folder_path, '*.xml'))

    filtered_files = []
    for file in all_xml_files:
        # Extract the year information from the file name
        file_name_parts = os.path.basename(file).split('_')
        file_start_year = int(file_name_parts[1])
        file_end_year = int(file_name_parts[5])

        # Check if the file's year range overlaps with the user-specified range
        if file_end_year >= start_year and file_start_year <= end_year:
            filtered_files.append(file)

    return filtered_files

if __name__ == "__main__":
    
    # Example usage for specific files
    # xml_file_path = 'NO1_2023_10_02_to_2023_10_08_day_ahead_prices.xml'  # Replace with your XML file path
    
    area_code = input("Enter the area code (e.g., 'NO1'): ").strip().upper()

    if not check_area_code_folder(area_code):
        print(f"No data folder found for area code {area_code}. Exiting.")
        exit()

    start_year = int(input("Enter the start year (YYYY): "))
    end_year = int(input("Enter the end year (YYYY): "))

    user_choice = input("Choose an option: 'all', 'first X', 'last X', or 'random X' files: ").strip().lower()

    # Filter XML files once here
    xml_files = filter_xml_files_by_year(area_code, start_year, end_year)

    if user_choice == 'all':
        process_files(xml_files)
        print("Processed all relevant files in the specified area code directory.")

    elif user_choice.startswith('first'):
        num_files = int(user_choice.split()[1])
        first_x_files = sorted(xml_files)[:num_files]
        process_files(first_x_files)
        print(f"Processed the first {num_files} files in the specified area code directory.")

    elif user_choice.startswith('last'):
        num_files = int(user_choice.split()[1])
        last_x_files = sorted(xml_files)[-num_files:]
        process_files(last_x_files)
        print(f"Processed the last {num_files} files in the specified area code directory.")

    elif user_choice.startswith('random'):
        num_files = int(user_choice.split()[1])
        random_x_files = random.sample(xml_files, min(num_files, len(xml_files)))
        process_files(random_x_files)
        print(f"Processed a random selection of {num_files} files from the specified area code directory.")

    else:
        print("Invalid input. Please enter one of the specified options.")