# weather_data.py

from noaa_sdk import NOAA
import pandas as pd
from datetime import datetime, timedelta

noaa = NOAA()

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and 'value' in v:
            items.append((new_key, v['value']))
        elif isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_weather_data(zipcode, country, start_date, end_date):
    res = noaa.get_observations(zipcode, country, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    data = []
    for observation in res:
        flattened = flatten_dict(observation)
        data.append(flattened)
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    return df