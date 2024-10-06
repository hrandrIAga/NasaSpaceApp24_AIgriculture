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
import pandas as pd


def calculate_daily_mean(df, column):
    return df.groupby(df.index.date)[column].mean()

def calculate_mean_last_5_days(daily_means):
    return daily_means.tail(5).mean()

def calculate_logit(meanrh, meanat):
    return -11.4041 + (0.0894 * meanrh) + (0.1932 * meanat)

def calculate_dollar_spot_risk(logit):
    return (math.exp(logit) / (1 + math.exp(logit))) * 100

def get_dollar_spot_risk(zipcode, country, date):
    end_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=4)
    df = get_weather_data(zipcode, country, start_date, end_date)
    
    # Ensure the index is a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Calculate daily means
    daily_rh = calculate_daily_mean(df, 'relativeHumidity')
    daily_temp = calculate_daily_mean(df, 'temperature')
    
    # Calculate 5-day means
    meanrh = calculate_mean_last_5_days(daily_rh)
    meanat = calculate_mean_last_5_days(daily_temp)
    
    logit = calculate_logit(meanrh, meanat)
    dollar_spot_risk = calculate_dollar_spot_risk(logit)
    
    return dollar_spot_risk
