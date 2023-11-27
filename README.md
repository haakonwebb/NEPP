# NEPP - Norwegian Electricity Price Predictor

NEPP (Norwegian Electricity Price Predictor) is a machine learning-based prediction model that forecasts future electricity prices in Norway's five regions using statistical data and advanced analytics.

## Table of Contents
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

Here's a brief overview of the project's file structure:
```
Portfolio_Elec_Model/
│
├── data/
│ ├── raw/ # Raw data storage
│ └── processed/ # Processed data
│ ├── cleaned/ # Cleaned data
│ ├── normalized/ # Normalized data
│ └── preprocessed/ # Preprocessed data
│
├── src/
│ ├── init.py # Initialization script
│ ├── config.py # Configuration settings
│ ├── data_cleaner.py # Data cleaning script
│ ├── data_fetcher.py # Data fetching script
│ ├── data_loader.py # Data loading script
│ ├── data_normalizer.py # Data normalization script
│ ├── data_preprocessor.py# Data preprocessing script
│ ├── data_processing_tracker.py # Data processing tracking
│ ├── main.py # Main script for running the project
│ ├── model.py # Model definition
│ ├── train.py # Model training script
│ └── utils.py # Utility functions
│
├── outputs/
│ ├── models/ # Model storage
│ └── figures/ # Generated figures and plots
│
├── tests/
│ └── test_data_preprocessor.py # Data processing tests
│
├── .env # Environment variables
├── .gitignore # Git ignore file
├── LICENSE # License details
├── README.md # Project overview (this file)
└── requirements.txt # Project dependencies
```

## Installation

To set up the NEPP project on your local machine, follow these steps:

1. **Clone the Repository:**
```
git clone https://github.com/haakonwebb/NEPP.git
cd Portfolio_Elec_Model
```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**
```
python -m venv venv
source venv/bin/activate # For Windows use venv\Scripts\activate
```


3. **Install Dependencies:**
```
pip install -r requirements.txt
```
Or run init.py


4. **Environment Variables:**
- Create your `.env` file.
```
touch .env
```
- Add enviroment variable ot the '.env' file.
```
ENTSOE_API_KEY=your_entsoe_api_key_here
```

## Usage

To run the NEPP project, follow these steps:

1. **Initialize the Project:**
- Run `python src/__init__.py` to create the necessary folder structure and install dependencies.

2. **Data Fetching and Processing:**
- Execute the data fetching, preprocessing, cleaning, and normalization scripts.

3. **Model Training:**
- Run the training script with the necessary parameters.

4. **Prediction and Analysis:**
- Use the main script or model scripts to perform predictions and analyses.

## License

This project is licensed under the GNU GPLv3. See the [LICENSE](LICENSE) file for more details.
