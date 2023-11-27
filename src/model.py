# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

def create_model(input_shape, num_outputs=1, units=50, dropout_rate=0.2):
    """
    Create and return a LSTM model for time series prediction.

    Args:
    input_shape (tuple): The shape of the input data (e.g., (24, number_of_features)).
    num_outputs (int): The number of output neurons. Default is 1 for a single output.
    units (int): The number of units in the LSTM layers.
    dropout_rate (float): Dropout rate for regularization.

    Returns:
    A compiled Keras model.
    """
    model = Sequential()

    # LSTM layer(s)
    model.add(LSTM(units, input_shape=input_shape, return_sequences=True))
    model.add(Dropout(dropout_rate))
    model.add(LSTM(units, return_sequences=False))
    model.add(Dropout(dropout_rate))

    # Output layer - Adjust for the number of outputs
    model.add(Dense(num_outputs))  # Configurable for multiple outputs

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])  # Using MSE for regression

    return model