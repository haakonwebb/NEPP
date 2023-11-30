# Copyright (C) 2023 Haakon Vollheim Webb
# This file is part of NEPP which is released under GNU GPLv3.
# See file LICENSE or go to https://www.gnu.org/licenses/gpl-3.0.html for full license details.

import os
from entsoe import EntsoeRawClient
import pandas as pd
from dotenv import load_dotenv
import time
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import config

# Load environment variables from .env
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("ENTSOE_API_KEY")

# Norwegian bidding zones as a tuple
area_codes = {
    "NO1": "10YNO-1--------2",  # NO1 Eastern Norway
    "NO2": "10YNO-2--------T",  # NO2 Southern Norway
    "NO3": "10YNO-3--------J",  # NO3 Central Norway
    "NO4": "10YNO-4--------9",  # NO4 Northern Norway
    "NO5": "10Y1001A1001A48H"   # NO5 Western Norway
}

client = EntsoeRawClient(api_key=api_key)

def fetch_data(start_date, end_date, area_code_name):
    country_code = area_codes.get(area_code_name)
    if not country_code:
        print(f"Invalid area code name: {area_code_name}")
        return

    # Adjust start and end times to Timestamp
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    max_days_per_request = 370
    current = start

    # Create subfolder for area code if it doesn't exist
    area_code_folder = os.path.join(config.DATA_RAW_DIR, area_code_name)
    os.makedirs(area_code_folder, exist_ok=True)

    while current < end:
        interval_end = min(current + pd.DateOffset(days=max_days_per_request - 1), end)
        print(f"Fetching data for {area_code_name}: {current} to {interval_end}...")

        try:
            xml_string = client.query_day_ahead_prices(country_code, current, interval_end)
            filename = f"{area_code_name}_{current.strftime('%Y_%m_%d')}_to_{interval_end.strftime('%Y_%m_%d')}_day_ahead_prices.xml"
            output_file_path = os.path.join(area_code_folder, filename)

            with open(output_file_path, 'w') as f:
                f.write(xml_string)

            print(f"Data saved to {output_file_path}")

        except Exception as e:
            print(f"Failed to fetch data: {e}")

        # Set current to the day after interval_end
        current = interval_end + pd.DateOffset(minutes=1)

def fetch_data_with_retries(start_date, end_date, area_code_name, max_retries=5, delay=10):
    attempts = 0
    while attempts < max_retries:
        try:
            fetch_data(start_date, end_date, area_code_name)
            return  # Successful fetch, exit function
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            attempts += 1
            print(f"Attempt {attempts}/{max_retries} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)

    print("Max retries reached. Exiting.")

if __name__ == "__main__":
    """
    A single request can only contain 370 doucments per request due to the limitations on API.
    Therefore when querying dates/periods longer than one year(roughly) the code will split
    the dates into an appropriate amount of requests.
    Example usage is fetch_data_with_retries(StartDate(YYYYMMDD), EndDate(YYYYMMDD), Area_code(NO#))
    """
    fetch_data_with_retries('20220101', '20221231', 'NO3')