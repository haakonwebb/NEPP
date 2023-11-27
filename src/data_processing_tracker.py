# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

def update_file_metadata(file_path, new_stage):
    """
    Update the metadata of a file to include a new processing stage.

    Parameters:
    file_path (str): Path to the file.
    new_stage (str): The processing stage to add (e.g., 'preprocessed').
    """
    try:
        with open(file_path, 'r+') as file:
            content = file.readlines()
            if len(content) > 0:
                stages = content[0].strip().split(',')
                if new_stage not in stages:
                    stages.append(new_stage)
                    content[0] = ','.join(stages) + '\n'
            else:
                content.insert(0, new_stage + '\n')
            file.seek(0)
            file.writelines(content)
    except IOError as e:
        print(f"Error updating file metadata: {e}")

def check_processing_stage(file_path, required_stage):
    """
    Check if a file has undergone a specific processing stage.

    Parameters:
    file_path (str): Path to the file.
    required_stage (str): The processing stage to check (e.g., 'cleaned').

    Returns:
    bool: True if the stage is present, False otherwise.
    """
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            return required_stage in first_line.split(',')
    except IOError as e:
        print(f"Error reading file metadata: {e}")
        return False