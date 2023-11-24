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
    df['price'].fillna(method='ffill', inplace=True)  # Forward fill for price

    # Correcting data types
    df['period_start'] = pd.to_datetime(df['period_start'])
    df['period_end'] = pd.to_datetime(df['period_end'])
    df['price'] = df['price'].astype(float)

    # Filter unnecessary data (if any)
    # df.drop(['unnecessary_column'], axis=1, inplace=True)

    return df

def clean_file(file_path):
    if check_processing_stage(file_path, 'preprocessed'):
        df = pd.read_csv(file_path)
        cleaned_df = clean_data(df)
        new_file_path = file_path.replace('_preprocessed.csv', '_cleaned.csv')
        save_df_to_csv(cleaned_df, new_file_path)  # Using the imported function
        update_file_metadata(new_file_path, 'cleaned')
        print(f"File {file_path} has been cleaned and saved as {new_file_path}.")
    else:
        print(f"File {file_path} has not been preprocessed. Skipping.")

if __name__ == "__main__":
    preprocessed_files = os.path.join(config.DATA_PROCESSED_DIR, '*_preprocessed.csv')
    for file_path in glob.glob(preprocessed_files):
        clean_file(file_path)