# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import os

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