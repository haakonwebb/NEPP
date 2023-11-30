import pandas as pd
import os
import config

def load_data(year, area_code, stage='normalized', specific_date=None):
    """
    Load CSV files from a specific year and area code within a processing stage.
    Optionally filter data to a specific date.

    Parameters:
    year (int): Year of the data to be loaded.
    area_code (str): The area code for the data.
    stage (str): Processing stage folder ('preprocessed', 'cleaned', 'normalized').
    specific_date (str, optional): Specific date to filter data in 'YYYYMMDD' format.

    Returns:
    DataFrame: A single DataFrame containing all data for the specified year and area code.
    """
    folder_path = os.path.join(config.DATA_PROCESSED_DIR, stage, area_code)
    file_path = os.path.join(folder_path, f"{area_code}_{year}.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        # Filter for a specific date if provided
        if specific_date:
            df['period_start'] = pd.to_datetime(df['period_start'])
            df = df[df['period_start'].dt.strftime('%Y%m%d') == specific_date]

        return df
    else:
        print(f"No data found for year {year} and area code {area_code} in {stage} stage.")
        return None

# Example usage
if __name__ == "__main__":
    year = 2023
    area_code = "NO2"
    specific_date = "20230915"  # Example date in 'YYYYMMDD' format
    data_for_specific_date = load_data(year, area_code, 'normalized', specific_date)
    if data_for_specific_date is not None:
        print(f"Loaded data for {year}, {area_code}, on {specific_date}: {data_for_specific_date.shape}")