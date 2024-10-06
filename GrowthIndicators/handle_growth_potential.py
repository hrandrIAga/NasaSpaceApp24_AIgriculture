# /home/hagamaya/Desktop/NasaSpaceApp24/HandleGrowthIndicators/handle_growth_potential.py

import sys
import os

# Add the parent directory of HandleGrowthIndicators to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Now import the module using the correct file name
from get_weather_data import get_weather_data

import json
from datetime import datetime, timedelta
import math

def calculate_growth_potential(temp, plant_type):
    if plant_type == 'C3':
        t0 = 20
        var = 5.5
    elif plant_type == 'C4':
        t0 = 31
        var = 7
    else:
        raise ValueError("plant_type must be either 'C3' or 'C4'")
    
    return math.exp(-0.5 * ((temp - t0) / var) ** 2)

def getGrowthPotential24h(zipcode, country, date, plant_type):
    start_date = datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    
    df = get_weather_data(zipcode, country, start_date, end_date)
    
    gp_values = {}
    for _, row in df.iterrows():
        timestamp = row['timestamp'].strftime('%Y-%m-%dT%H:%M:%S%z')
        temp = row['temperature']
        gp = calculate_growth_potential(temp, plant_type)
        gp_values[timestamp] = round(gp, 4)
    
    return json.dumps(gp_values)

def getGrowthPotentialDay(zipcode, country, date, plant_type):
    start_date = datetime.strptime(date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    
    df = get_weather_data(zipcode, country, start_date, end_date)
    
    df['growth_potential'] = df['temperature'].apply(lambda x: calculate_growth_potential(x, plant_type))
    daily_gp = df.groupby(df['timestamp'].dt.date)['growth_potential'].mean()
    
    gp_values = {str(date): round(gp, 4) for date, gp in daily_gp.items()}
    
    return json.dumps(gp_values)

# For debugging: print the Python path
print(sys.path)

# For debugging: print the contents of the parent directory
print(os.listdir(parent_dir))