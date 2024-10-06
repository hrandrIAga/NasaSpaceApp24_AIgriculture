import sys
import os
# Add the parent directory of HandleGrowthIndicators to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
# Now import the module using the correct file name
from get_weather_data import get_weather_data
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def calculate_gdd(tmin, tmax, plant_type):
    if plant_type == 'C3':
        tbase = 6
    elif plant_type == 'C4':
        tbase = 11
    else:
        raise ValueError("plant_type must be either 'C3' or 'C4'")
    return ((tmax + np.maximum(tmin, tbase)) / 2) - tbase


def get_gdd_daily(zipcode, country, date, plant_type):
    start_date = datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date
    df = get_weather_data(zipcode, country, start_date, end_date)
    
    # Group by day of timestamp
    tmin = df.groupby(df['timestamp'].dt.date)['temperature'].min()
    tmax = df.groupby(df['timestamp'].dt.date)['temperature'].max()
    
    gdd = calculate_gdd(tmin, tmax, plant_type)
    
    # Convert the result to a dictionary with string keys, then to JSON
    result = {k.strftime('%Y-%m-%d'): float(v) for k, v in gdd.items()}
    return json.dumps(result)

def get_gdd_cumulative(zipcode, country, start_date, plant_type):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.now()
    df = get_weather_data(zipcode, country, start_date, end_date)
    
    daily_gdd = []
    cumulative_gdd = 0
    
    for date, group in df.groupby(df['timestamp'].dt.date):
        tmin = group['temperature'].min()
        tmax = group['temperature'].max()
        daily_gdd_value = calculate_gdd(pd.Series([tmin]), pd.Series([tmax]), plant_type).item()
        cumulative_gdd += daily_gdd_value
        daily_gdd.append({
            'date': date.strftime('%Y-%m-%d'),
            'daily_gdd': float(daily_gdd_value),
            'cumulative_gdd': float(cumulative_gdd)
        })
    
    return json.dumps(daily_gdd)
