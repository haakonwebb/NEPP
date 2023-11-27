# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import numpy as np
import pandas as pd
from model import create_model
from data_loader import load_data
from config import MODEL_SAVE_PATH, TRAINING_EPOCHS, BATCH_SIZE

def prepare_sequences(data, look_back=24):
    """
    Create sequences of 24-hour windows to predict the next hour.

    Args:
    data (np.array): Array of input features.
    look_back (int): Number of timesteps to look back for prediction.

    Returns:
    Tuple of (input_sequences, target_prices).
    """
    input_sequences, target_prices = [], []
    for i in range(len(data) - look_back):
        # Extracting the sequence of features (all columns except the last one)
        sequence = data[i:(i + look_back), :-1]
        # Ensure sequence is numeric
        sequence = sequence.astype(np.float32)

        # Extracting the target price (last column)
        target = data[i + look_back, -1]
        # Ensure target is numeric
        target = float(target)

        input_sequences.append(sequence)
        target_prices.append(target)

    return np.array(input_sequences), np.array(target_prices)

def train_model(years, area_code):
    # Initialize model
    num_features = 8  # Update this based on your actual number of features
    num_outputs = 1  # For single regression target
    model = create_model(input_shape=(24, num_features), num_outputs=num_outputs)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # Train model for each specified year
    for year in years:
        print(f"Training on data from year: {year} and area code: {area_code}")
        year_data = load_data(int(year), area_code, 'normalized')  # Load normalized data

        if year_data is not None:
            train_sequences, train_targets = prepare_sequences(year_data.values)
            model.fit(train_sequences, train_targets, epochs=TRAINING_EPOCHS, batch_size=BATCH_SIZE)
        else:
            print(f"No data available for year {year} and area code {area_code}.")

    # Validate model using data from 2022
    validation_data = load_data(2022, 'normalized')  # Load normalized data for validation year
    validation_data = pd.concat(validation_data).values
    validation_sequences, validation_targets = prepare_sequences(validation_data)

    validation_results = model.evaluate(validation_sequences, validation_targets)
    print(f"Validation Results - Loss: {validation_results[0]}, MAE: {validation_results[1]}")

    # Save the trained model
    model.save(MODEL_SAVE_PATH)

if __name__ == "__main__":
    input_years = input("Enter the years for training (comma-separated, e.g., 2017,2018,2019): ")
    input_area_code = input("Enter the area code (e.g., NO1): ")
    years = [int(year.strip()) for year in input_years.split(',')]
    train_model(years, input_area_code)