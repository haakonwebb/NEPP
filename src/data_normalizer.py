# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import pandas as pd
import os
import glob
from sklearn.preprocessing import MinMaxScaler
import config
import numpy as np

def extract_time_features(df):
    # Convert 'period_start' to datetime if it's not already
    df['period_start'] = pd.to_datetime(df['period_start'])

    # Extract time features
    df['hour'] = df['period_start'].dt.hour
    df['day_of_week'] = df['period_start'].dt.dayofweek
    df['day_of_month'] = df['period_start'].dt.day
    df['month'] = df['period_start'].dt.month
    df['year'] = df['period_start'].dt.year

    # Cyclical encoding for hour and day_of_week
    df['hour_sin'] = np.sin(df['hour'] * (2 * np.pi / 24))
    df['hour_cos'] = np.cos(df['hour'] * (2 * np.pi / 24))
    df['day_of_week_sin'] = np.sin(df['day_of_week'] * (2 * np.pi / 7))
    df['day_of_week_cos'] = np.cos(df['day_of_week'] * (2 * np.pi / 7))

    # Optionally, drop the 'period_end' column if it's redundant
    df.drop(['period_start', 'period_end'], axis=1, inplace=True)

    return df

def normalize_data(df):
    # Extract and encode time features first
    df = extract_time_features(df)

    # Now select the columns to keep for normalization
    columns_to_keep = ['price', 'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 'day_of_month', 'month', 'year']

    # Create a copy of the DataFrame to keep only necessary columns
    df_filtered = df[columns_to_keep].copy()

    # Initialize a scaler
    scaler = MinMaxScaler()

    # Normalize the 'price' column
    df_filtered['price'] = scaler.fit_transform(df_filtered[['price']])

    # Optionally, if other columns need normalization, normalize them here

    return df_filtered

def normalize_file(file_path, area_code_folder):
    # Load dataset
    df = pd.read_csv(file_path)

    # Apply normalization
    normalized_df = normalize_data(df)

    # Save the normalized data in the corresponding area code subfolder
    normalized_file_path = os.path.join(area_code_folder, os.path.basename(file_path))
    normalized_df.to_csv(normalized_file_path, index=False)
    print(f"File {file_path} has been normalized and saved as {normalized_file_path}")

if __name__ == "__main__":
    area_code = input("Enter the area code for data normalization (e.g., 'NO1'): ").strip().upper()
    area_code_folder = os.path.join(config.DATA_CLEANED_DIR, area_code)

    # Check if the specified area code folder exists
    if not os.path.exists(area_code_folder):
        print(f"No cleaned data found for area code {area_code}. Exiting.")
        exit()

    # Create corresponding area code subfolder in normalized data directory
    normalized_area_code_folder = os.path.join(config.DATA_NORMALIZED_DIR, area_code)
    os.makedirs(normalized_area_code_folder, exist_ok=True)

    # Iterate through each file in the specified area code subfolder
    cleaned_files = glob.glob(os.path.join(area_code_folder, '*.csv'))
    for file_path in cleaned_files:
        normalize_file(file_path, normalized_area_code_folder)