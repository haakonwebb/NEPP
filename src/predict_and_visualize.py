# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import matplotlib.pyplot as plt
from keras.models import load_model
from data_fetcher import fetch_data_with_retries
from data_preprocessor import process_files, filter_xml_files_by_year
from data_cleaner import clean_file
from data_normalizer import normalize_file
from data_loader import load_data
import config 
import numpy as np
from datetime import datetime, timedelta
import pytz
import os


def fetch_and_process_recent_data(area_code):
    # Calculate tomorrow's date in UTC+1
    tomorrow_utc_plus_1 = datetime.now(pytz.utc) + timedelta(days=1, hours=1)

    # Convert dates to 'YYYYMMDD' format
    start_date_str = tomorrow_utc_plus_1.strftime('%Y%m%d')
    current_year = tomorrow_utc_plus_1.strftime('%Y')

    fetch_data_with_retries(start_date_str, start_date_str, area_code)

    xml_files = filter_xml_files_by_year(area_code, int(current_year), int(current_year))
    process_files(xml_files)

    # File path for the specific year's data
    file_path = os.path.join(config.DATA_PREPROCESSED_DIR, area_code, f"{area_code}_{current_year}.csv")

    # Check if the file exists
    if os.path.exists(file_path):
        # Clean the specific file
        cleaned_area_code_folder = os.path.join(config.DATA_CLEANED_DIR, area_code)
        os.makedirs(cleaned_area_code_folder, exist_ok=True)
        clean_file(file_path, cleaned_area_code_folder)
    else:
        print(f"File not found: {file_path}")
        return None
    
    # File path for the specific year's data in the cleaned directory
    file_path = os.path.join(config.DATA_CLEANED_DIR, area_code, f"{area_code}_{current_year}.csv")

    # Check if the file exists
    if os.path.exists(file_path):
        # Normalize the specific file
        normalized_area_code_folder = os.path.join(config.DATA_NORMALIZED_DIR, area_code)
        os.makedirs(normalized_area_code_folder, exist_ok=True)
        normalize_file(file_path, normalized_area_code_folder)
    else:
        print(f"File not found: {file_path}")
        return None

    data_for_tomorrow = load_data(int(current_year), area_code, 'normalized', start_date_str)

    return data_for_tomorrow


def predict_next_48_hours(model_path, recent_data, next_day_actual_prices):
    # Load model
    model = load_model(model_path)

    # Predict the next 24 hours using recent data
    first_day_predictions = model.predict(recent_data)

    # Prepare data for the following day's prediction
    # Replace the last 24 hours of recent_data with the actual prices of the next day
    following_day_input = np.roll(recent_data, -24, axis=0)
    following_day_input[-24:, -1] = next_day_actual_prices  # Assuming 'price' is the last column

    # Predict the following day (day after next)
    second_day_predictions = model.predict(following_day_input)

    return first_day_predictions, second_day_predictions


def visualize_predictions(predictions, actual_prices):
    plt.figure(figsize=(12, 6))
    plt.plot(predictions, label='Predicted Prices')
    plt.plot(actual_prices, label='Actual Prices', alpha=0.7)

    plt.xlabel('Time')
    plt.ylabel('Electricity Price')
    plt.title('Electricity Price Prediction vs Actual for the Next 24 Hours')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # Fetch and process recent data
    recent_data = fetch_and_process_recent_data('NO2')

    # Assuming next_day_actual_prices will be provided or fetched from somewhere
    next_day_actual_prices = None # Placeholder, replace with actual data fetching if available

    # Predict for the next 48 hours
    predictions_48h = predict_next_48_hours(config.MODEL_SAVE_PATH+'trained_model1.keras', recent_data, next_day_actual_prices)

    # Visualize predictions (modify as needed to handle 48h)
    visualize_predictions(predictions_48h[1], None)  # Second day predictions
    # Optionally visualize the first day predictions: visualize_predictions(predictions_48h[0], None)