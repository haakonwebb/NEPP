# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

# Configuration settings for the project

# Base directory for raw and processed data
BASE_DATA_DIR = 'data/'

# Subdirectories for different stages of data processing
DATA_RAW_DIR = BASE_DATA_DIR + 'raw/'
DATA_PROCESSED_DIR = BASE_DATA_DIR + 'processed/'
DATA_PREPROCESSED_DIR = DATA_PROCESSED_DIR + 'preprocessed/'
DATA_CLEANED_DIR = DATA_PROCESSED_DIR + 'cleaned/'
DATA_NORMALIZED_DIR = DATA_PROCESSED_DIR + 'normalized/'

# Other configurations
MODEL_SAVE_PATH = 'outputs/models/'
TRAINING_EPOCHS = 100  #It seems like this might need to be updated later on, increasing the number of EPOCH's
BATCH_SIZE = 32