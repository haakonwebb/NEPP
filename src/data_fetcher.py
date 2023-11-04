# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import os
from entsoe import EntsoeRawClient
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("ENTSOE_API_KEY")

# Norwegian bidding zones as individual variables
NO1 = "10YNO-1--------2"  # NO1 Eastern Norway
NO2 = "10YNO-2--------T"  # NO2 Southern Norway
NO3 = "10YNO-3--------J"  # NO3 Central Norway
NO4 = "10YNO-4--------9"  # NO4 Northern Norway
NO5 = "10Y1001A1001A48H"  # NO5 Western Norway

client = EntsoeRawClient(api_key=api_key)

def fetch_data(start_date, end_date, country_code):
    start = pd.Timestamp(start_date, tz='Europe/Oslo')
    end = pd.Timestamp(end_date, tz='Europe/Oslo')
    xml_string = client.query_day_ahead_prices(country_code, start, end)

    # Directory path for raw data
    raw_data_directory = os.path.join('data', 'raw')

    # Ensure the directory exists
    os.makedirs(raw_data_directory, exist_ok=True)

    # Define the path for the output file
    output_file_path = os.path.join(raw_data_directory, f'{country_code}_{start_date}_to_{end_date}_prices.xml')

    # Write the data to the file
    with open(output_file_path, 'w') as f:
        f.write(xml_string)

if __name__ == "__main__":
    # Example usage:
    fetch_data('20231102', '20231103', NO5)
