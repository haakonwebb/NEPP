# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import pandas as pd
import os
import glob
import config

def load_all_data():
    """
    Load all CSV files in the processed data directory into pandas DataFrames.

    Returns:
    dict: A dictionary where keys are file names and values are DataFrames.
    """
    file_path_pattern = os.path.join(config.DATA_PROCESSED_DIR, '*.csv')
    csv_files = glob.glob(file_path_pattern)

    data_frames = {}
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            file_name = os.path.basename(csv_file)
            data_frames[file_name] = df
            print(f"Loaded {file_name}: {df.shape[0]} rows, {df.shape[1]} columns")
        except Exception as e:
            print(f"Error loading file {csv_file}: {e}")

    return data_frames

if __name__ == "__main__":
    # Load all data and print the number of files loaded
    all_data = load_all_data()
    print(f"Total files loaded: {len(all_data)}")
