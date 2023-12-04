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
    current_time_utc_plus_1 = datetime.now(pytz.utc) + timedelta(hours=1)

    if current_time_utc_plus_1.hour > 18:
        data_date = current_time_utc_plus_1 + timedelta(days=1)
    else:
        data_date = current_time_utc_plus_1

    data_date_str = data_date.strftime('%Y%m%d')
    current_year = data_date.strftime('%Y')
    end_date = data_date + timedelta(days=1)
    end_date_str = end_date.strftime('%Y%m%d')


    normalized_file_path = os.path.join(config.DATA_NORMALIZED_DIR, area_code, f"{area_code}_{current_year}.csv")

    # Check if normalized data for the specific date exists
    if os.path.exists(normalized_file_path):
        existing_data = load_data(int(current_year), area_code, 'normalized', specific_date=data_date_str, return_array=True)
        if existing_data is not None and not existing_data.size == 0:
            print(f"Normalized data for {data_date_str} already exists. Loading data.")
            return existing_data

    # Data for the specific date does not exist, proceed to fetch and process
    fetch_data_with_retries(data_date_str, end_date_str, area_code)

    xml_files = filter_xml_files_by_year(area_code, int(current_year), int(current_year))
    process_files(xml_files)

    # Path for the specific year's preprocessed and cleaned data
    preprocessed_file_path = os.path.join(config.DATA_PREPROCESSED_DIR, area_code, f"{area_code}_{current_year}.csv")
    cleaned_file_path = os.path.join(config.DATA_CLEANED_DIR, area_code, f"{area_code}_{current_year}.csv")

    # Clean the specific preprocessed file if it exists
    if os.path.exists(preprocessed_file_path):
        cleaned_area_code_folder = os.path.join(config.DATA_CLEANED_DIR, area_code)
        os.makedirs(cleaned_area_code_folder, exist_ok=True)
        clean_file(preprocessed_file_path, cleaned_area_code_folder)
    else:
        print(f"Preprocessed file not found: {preprocessed_file_path}")
        return None

    # Normalize the specific cleaned file if it exists
    if os.path.exists(cleaned_file_path):
        normalized_area_code_folder = os.path.join(config.DATA_NORMALIZED_DIR, area_code)
        os.makedirs(normalized_area_code_folder, exist_ok=True)
        normalize_file(cleaned_file_path, normalized_area_code_folder)
    else:
        print(f"Cleaned file not found: {cleaned_file_path}")
        return None

    # Load the normalized data for the specified date
    return load_data(int(current_year), area_code, 'normalized', specific_date=data_date_str, return_array=True)

def predict_next_24_hours(model, recent_data):
    model = load_model(model)

    predictions = []
    current_input = recent_data
    
    # Predict iteratively
    for _ in range(24):
        # Predict the next hour
        next_hour_prediction = model.predict(current_input)
        predictions.append(next_hour_prediction[0, 0])  # Assuming the prediction shape is (1, 1)
        
        # Update current_input to include the new prediction
        current_input = np.roll(current_input, -1, axis=1)
        current_input[0, -1, 0] = next_hour_prediction  # Set the last value to the new prediction
    
    return np.array(predictions)

def visualize_predictions(predictions):
    plt.figure(figsize=(12, 6))
    plt.plot(predictions, label='Predicted Prices')

    plt.xlabel('Time')
    plt.ylabel('Electricity Price')
    plt.title('Electricity Price Prediction for the Next 24 Hours')
    plt.legend()
    plt.show()

def get_latest_data_date(data):
    """
    Extract the latest date from the reshaped data.

    Args:
    data (np.array): The reshaped data array.

    Returns:
    datetime: The latest date in the data.
    """
    # Assuming the last data point's last three features are year, month, and day
    last_data_point = data[-1, -1]  # Last row of the last data point
    latest_year = int(last_data_point[-1])
    latest_month = int(last_data_point[-2])
    latest_day = int(last_data_point[-3])

    print(f"Year: {latest_year}, Month: {latest_month}, Day: {latest_day}")

    return datetime(latest_year, latest_month, latest_day)

def reshape_data_for_prediction(data, look_back=24):
    """
    Reshape the data to the format suitable for model prediction.

    Args:
    data (np.array): Array of input features including the price column.
    look_back (int): Number of timesteps to look back for prediction.

    Returns:
    np.array: Reshaped data ready for prediction.
    """
    # Assuming the first column is the price, exclude it from features
    feature_data = data[:, 1:]  # Exclude the price column
    
    # Initialize an array to hold the reshaped data
    reshaped_data = []

    # Generate sequences for prediction
    for i in range(len(feature_data) - look_back + 1):
        sequence = feature_data[i:(i + look_back)]
        reshaped_data.append(sequence)

    return np.array(reshaped_data)

if __name__ == "__main__":
    # Fetch and process recent data
    recent_data = fetch_and_process_recent_data('NO5')

    # Reshape data for prediction
    reshaped_recent_data = reshape_data_for_prediction(recent_data)

    # Get the current date in UTC+1
    current_time_utc_plus_1 = datetime.now(pytz.utc) + timedelta(hours=1)
    current_date = current_time_utc_plus_1.date()

    if reshaped_recent_data is not None:
        # Get the latest date from recent_data
        latest_data_date = get_latest_data_date(reshaped_recent_data).date()

        if latest_data_date == current_date:
            print('Data is for today, predict for tomorrow')
            next_day_predictions = predict_next_24_hours(config.MODEL_SAVE_PATH+'trained_model1.keras', reshaped_recent_data)
            visualize_predictions(next_day_predictions)
        elif latest_data_date < current_date:
            print('Data is for tomorrows date, predict for the next two days')
            next_two_days_predictions = predict_next_24_hours(config.MODEL_SAVE_PATH+'trained_model1.keras', reshaped_recent_data)
            visualize_predictions(next_two_days_predictions[1])  # Visualize second day's predictions