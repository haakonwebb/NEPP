import pandas as pd
import os
import config

def load_data(year, area_code, stage='normalized', specific_date=None, return_array=False):
    """
    Load CSV files from a specific year and area code within a processing stage.
    Optionally filter data to a specific date and return as a DataFrame or NumPy array.

    Parameters:
    year (int): Year of the data to be loaded.
    area_code (str): The area code for the data.
    stage (str): Processing stage folder ('preprocessed', 'cleaned', 'normalized').
    specific_date (str, optional): Specific date to filter data in 'YYYYMMDD' format.
    return_array (bool): If True, return data as a NumPy array, otherwise as a DataFrame.

    Returns:
    DataFrame or numpy.ndarray: Data as a DataFrame or a NumPy array.
    """
    folder_path = os.path.join(config.DATA_PROCESSED_DIR, stage, area_code)
    file_path = os.path.join(folder_path, f"{area_code}_{year}.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        if specific_date:
            specific_date_dt = pd.to_datetime(specific_date, format='%Y%m%d')
            day, month, year = specific_date_dt.day, specific_date_dt.month, specific_date_dt.year

            # Filter DataFrame based on day, month, and year
            df = df[(df['day_of_month'] == day) & (df['month'] == month) & (df['year'] == year)]

            if df.empty:
                # Return None if no data is found for the specific date
                return None

        return df.values if return_array else df
    else:
        print(f"No data found for year {year} and area code {area_code} in {stage} stage.")
        return None

# Example usage
if __name__ == "__main__":
    year = 2020
    area_code = "NO1"
    specific_date = "20201201"
    data_df = load_data(year, area_code, 'normalized', specific_date=specific_date)
    data_array = load_data(year, area_code, 'normalized', specific_date=specific_date, return_array=True)

    if data_df is not None:
        print(f"Loaded data as DataFrame for {year}, {area_code}, on {specific_date}: {data_df.shape}")
    if data_array is not None:
        print(f"Loaded data as NumPy array for {year}, {area_code}, on {specific_date}: {data_array.shape}")