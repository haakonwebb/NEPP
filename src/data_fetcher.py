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

# Norwegian bidding zones as a tuple
area_codes = {
    "NO1": "10YNO-1--------2",  # NO1 Eastern Norway
    "NO2": "10YNO-2--------T",  # NO2 Southern Norway
    "NO3": "10YNO-3--------J",  # NO3 Central Norway
    "NO4": "10YNO-4--------9",  # NO4 Northern Norway
    "NO5": "10Y1001A1001A48H"   # NO5 Western Norway
}


client = EntsoeRawClient(api_key=api_key)

def align_to_monday(date):
    """
    Adjusts a given date to the previous Monday if it's not already a Monday.

    Parameters:
    date (pd.Timestamp): The date to align.

    Returns:
    pd.Timestamp: The aligned date.
    """
    return date - pd.DateOffset(days=date.weekday())

def fetch_data(start_date, end_date, area_code_name):
    country_code = area_codes.get(area_code_name)
    if not country_code:
        print(f"Invalid area code name: {area_code_name}")
        return

    start = pd.Timestamp(start_date, tz='Europe/Oslo')
    end = pd.Timestamp(end_date, tz='Europe/Oslo')
    current = align_to_monday(start)

    while current < end:
        # Set the end of the week to the nearest Sunday, including all of Sunday
        week_end = min(current + pd.DateOffset(days=6, hours=23, minutes=59, seconds=59), end)
        print(f"Fetching data from {current} to {week_end}...")

        xml_string = client.query_day_ahead_prices(country_code, current, week_end)

        # Save each week's data in a separate file
        raw_data_directory = os.path.join('data', 'raw')
        os.makedirs(raw_data_directory, exist_ok=True)

        # Format the filename with the year, month, and week number
        filename = f"{area_code_name}_Week{current.strftime('%W')}_{current.strftime('%Y_%m_%d')}_to_{week_end.strftime('%Y_%m_%d')}_prices.xml"
        output_file_path = os.path.join(raw_data_directory, filename)

        with open(output_file_path, 'w') as f:
            f.write(xml_string)

        print(f"Data saved to {output_file_path}")
        # Move to the next Monday
        current = week_end + pd.DateOffset(minutes=1) if week_end < end else end

if __name__ == "__main__":
    # Example usage
    fetch_data('20231002', '20231102', 'NO1')