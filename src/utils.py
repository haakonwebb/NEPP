# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import os
from data_processing_tracker import update_file_metadata

def save_df_to_csv(df, file_path, overwrite=False):
    """
    Save a DataFrame to a CSV file.

    Parameters:
    df (DataFrame): The DataFrame to save.
    file_path (str): The path to the file where the DataFrame should be saved.
    overwrite (bool): If True, overwrite the existing file, otherwise append to it.
    """
    if overwrite or not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode='a', index=False, header=False)
    
    update_file_metadata(file_path, os.path.basename(file_path).split('_')[0])