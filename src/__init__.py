# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import os
import subprocess

def create_folder_structure(base_path):
    folders = [
        'data/raw',
        'data/processed',
        'data/processed/cleaned',
        'data/processed/normalized',
        'data/processed/preprocessed',
        'outputs/models',
        'outputs/figures',
        'tests'
    ]

    for folder in folders:
        path = os.path.join(base_path, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created folder: {path}")
        else:
            print(f"Folder already exists: {path}")

def install_requirements(base_path):
    req_file = os.path.join(base_path, 'requirements.txt')
    if os.path.exists(req_file):
        print("Installing dependencies from requirements.txt...")
        subprocess.run(['pip', 'install', '-r', req_file], check=True)
    else:
        print("requirements.txt not found.")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.dirname(__file__))  # Points to 'Portfolio_Elec_Model'
    create_folder_structure(base_path)
    install_requirements(base_path)