# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import pandas as pd
import os
import config

def load_data(year, area_code, stage='normalized'):
    """
    Load CSV files from a specific year and area code within a processing stage.

    Parameters:
    year (int): Year of the data to be loaded.
    area_code (str): The area code for the data.
    stage (str): Processing stage folder ('preprocessed', 'cleaned', 'normalized').

    Returns:
    DataFrame: A single DataFrame containing all data for the specified year and area code.
    """
    folder_path = os.path.join(config.DATA_PROCESSED_DIR, stage, area_code)
    file_path = os.path.join(folder_path, f"{area_code}_{year}.csv")

    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"No data found for year {year} and area code {area_code} in {stage} stage.")
        return None

# Example usage
if __name__ == "__main__":
    # Load data for a specific year and area code from the 'normalized' folder
    year = 2020
    area_code = "NO1"
    normalized_data = load_data(year, area_code, 'normalized')
    if normalized_data is not None:
        print(f"Loaded data for {year}, {area_code}: {normalized_data.shape}")