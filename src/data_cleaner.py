# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import pandas as pd
import os
import glob
import config
from data_processing_tracker import update_file_metadata, check_processing_stage
from utils import save_df_to_csv

def clean_data(df):
    # Remove duplicate rows
    df = df.drop_duplicates()

    # Handle missing values
    df['price'].ffill(inplace=True)

    # Correcting data types
    df['period_start'] = pd.to_datetime(df['period_start'])
    df['period_end'] = pd.to_datetime(df['period_end'])
    df['price'] = df['price'].astype(float)

    # Filter unnecessary data (if any)
    # df.drop(['unnecessary_column'], axis=1, inplace=True)

    return df

def clean_file(file_path, area_code_folder):
    if check_processing_stage(file_path, 'preprocessed'):
        df = pd.read_csv(file_path)
        cleaned_df = clean_data(df)

        # Save the cleaned data in the corresponding area code subfolder
        cleaned_file_path = os.path.join(area_code_folder, os.path.basename(file_path))
        save_df_to_csv(cleaned_df, cleaned_file_path, overwrite=True)

        # Update metadata
        update_file_metadata(cleaned_file_path, 'cleaned')
        print(f"File {file_path} has been cleaned and saved in the cleaned directory.")
    else:
        print(f"File {file_path} has not been preprocessed. Skipping.")

if __name__ == "__main__":
    area_code = input("Enter the area code for data cleaning (e.g., 'NO1'): ").strip().upper()
    area_code_folder = os.path.join(config.DATA_PREPROCESSED_DIR, area_code)

    # Check if the specified area code folder exists
    if not os.path.exists(area_code_folder):
        print(f"No preprocessed data found for area code {area_code}. Exiting.")
        exit()

    # Create corresponding area code subfolder in cleaned data directory
    cleaned_area_code_folder = os.path.join(config.DATA_CLEANED_DIR, area_code)
    os.makedirs(cleaned_area_code_folder, exist_ok=True)

    # Iterate through each file in the specified area code subfolder
    preprocessed_files = glob.glob(os.path.join(area_code_folder, '*.csv'))
    for file_path in preprocessed_files:
        clean_file(file_path, cleaned_area_code_folder)