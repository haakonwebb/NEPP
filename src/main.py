# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

from data_fetcher import fetch_data_with_retries
from data_preprocessor import process_all_xml_files
from data_cleaner import clean_file
from data_normalizer import normalize_file
from train import train_model
import os, config

def main():
    area_code = input("Enter the area code (e.g., NO1): ").strip().upper()

    # Fetching Data
    if proceed_to_next_step(area_code, config.DATA_RAW_DIR, "fetching data"):
        fetch_data(area_code)

    # Preprocessing Data
    if proceed_to_next_step(area_code, config.DATA_PREPROCESSED_DIR, "preprocessing data"):
        preprocess_data(area_code)

    # Cleaning Data
    if proceed_to_next_step(area_code, config.DATA_CLEANED_DIR, "cleaning data"):
        clean_data(area_code)

    # Normalizing Data
    if proceed_to_next_step(area_code, config.DATA_NORMALIZED_DIR, "normalizing data"):
        normalize_data(area_code)

    # Training Model
    if input("Do you want to train the model? (yes/no): ").lower() == 'yes':
        years = input("Enter the years to train on (comma-separated, e.g., 2017,2018,2019): ")
        train_model(years.split(','), area_code)

def proceed_to_next_step(area_code, directory, stage):
    folder_path = os.path.join(directory, area_code)
    if os.path.exists(folder_path) and os.listdir(folder_path):
        choice = input(f"Data already exists in {folder_path}. Do you want to continue with {stage}, overwrite existing data, or skip? (continue/overwrite/skip): ").lower()
        if choice == 'overwrite':
            clear_directory(folder_path)
        return choice != 'skip'
    return True

def clear_directory(folder_path):
    for file in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, file))

def fetch_data(area_code):
    start_date = input("Enter the start date (YYYYMMDD): ")
    end_date = input("Enter the end date (YYYYMMDD): ")
    fetch_data_with_retries(start_date, end_date, area_code)

def preprocess_data(area_code):
    start_date = input("Enter the start date for preprocessing (YYYY-MM-DD): ")
    end_date = input("Enter the end date for preprocessing (YYYY-MM-DD): ")
    process_all_xml_files(area_code, start_date, end_date)

def clean_data(area_code):
    clean_file(area_code)

def normalize_data(area_code):
    normalize_file(area_code)

if __name__ == "__main__":
    main()