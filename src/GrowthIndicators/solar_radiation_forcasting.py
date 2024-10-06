import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

# Mock the get_weather_data function for testing
def get_weather_data(zipcode, country, start_date, end_date):
    # This is a mock function that returns dummy data for testing
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    data = {
        'timestamp': date_range,
        'temperature': np.random.uniform(15, 25, len(date_range)),
        'relativeHumidity': np.random.uniform(40, 80, len(date_range)),
        'windSpeed': np.random.uniform(0, 10, len(date_range))
    }
    return pd.DataFrame(data)

def get_solar_radiation_data(latitude, longitude, start_date, end_date):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON"
    response = requests.get(url)
    data = json.loads(response.text)
    return data['properties']['parameter']['ALLSKY_SFC_SW_DWN']

def predict_missing_data(data, days_to_predict=5):
    valid_data = {k: v for k, v in data.items() if v != -999}
    values = np.array(list(valid_data.values()))
    last_date = datetime.strptime(list(valid_data.keys())[-1], "%Y%m%d")
    
    previous_year_data = []
    for i in range(days_to_predict):
        date = last_date + timedelta(days=i+1)
        previous_year_date = (date - timedelta(days=365)).strftime("%Y%m%d")
        if previous_year_date in valid_data:
            previous_year_data.append(valid_data[previous_year_date])
        else:
            previous_year_data.append(np.mean(values[-30:]))
    
    X = np.arange(30).reshape(-1, 1)
    y = values[-30:]
    model = LinearRegression().fit(X, y)
    X_pred = np.arange(30, 30 + days_to_predict).reshape(-1, 1)
    linear_predictions = model.predict(X_pred)
    
    final_predictions = 0.5 * np.array(previous_year_data) + 0.5 * linear_predictions
    
    new_data = {}
    for i in range(days_to_predict):
        date = (last_date + timedelta(days=i+1)).strftime("%Y%m%d")
        new_data[date] = final_predictions[i] - 0.22
    
    return new_data

def get_solar_radiation(latitude, longitude, target_date):
    today = datetime.now().date()
    target_date = datetime.strptime(target_date, "%Y%m%d").date()
    
    if target_date >= today - timedelta(days=5):
        # Use prediction model
        end_date = today.strftime("%Y%m%d")
        start_date = (today - timedelta(days=400)).strftime("%Y%m%d")
        data = get_solar_radiation_data(latitude, longitude, start_date, end_date)
        valid_data = {k: v for k, v in data.items() if v != -999}
        days_to_predict = (target_date - today).days + 5
        predictions = predict_missing_data(valid_data, days_to_predict)
        solar_radiation_kwh = predictions.get(target_date.strftime("%Y%m%d"), None)
    else:
        # Use historical data
        start_date = target_date.strftime("%Y%m%d")
        end_date = start_date
        data = get_solar_radiation_data(latitude, longitude, start_date, end_date)
        solar_radiation_kwh = data.get(start_date, None)
    
    # Convert kWh/m²/day to MJ/m²/day
    if solar_radiation_kwh is not None:
        solar_radiation_mj = solar_radiation_kwh * 3.6
        return solar_radiation_mj
    else:
        return None

def preprocess_weather_data(weather_data):
    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(weather_data['timestamp']):
        weather_data['timestamp'] = pd.to_datetime(weather_data['timestamp'])
    
    # Group by date and calculate daily statistics
    daily_data = weather_data.groupby(weather_data['timestamp'].dt.date).agg({
        'temperature': ['mean', 'min', 'max'],
        'relativeHumidity': 'mean',
        'windSpeed': 'mean'
    })
    
    # Flatten column names
    daily_data.columns = ['_'.join(col).strip() for col in daily_data.columns.values]
    
    return daily_data

def calculate_etp(weather_data, solar_radiation):
    # Constants
    ALPHA = 0.23
    Z = 1  # Altitude in meters

    # Extract required data from weather_data
    T_mean = weather_data['temperature_mean']
    T_min = weather_data['temperature_min']
    T_max = weather_data['temperature_max']
    RH_mean = weather_data['relativeHumidity_mean']
    u_10 = weather_data['windSpeed_mean']

    # Calculate intermediate variables
    u_2 = 0.7 * u_10
    Rg_net = (1 - ALPHA) * solar_radiation
    es = 0.6108 * np.exp((17.27 * T_mean) / (237.3 + T_mean))
    ea = es * RH_mean / 100
    delta = (4098 * es) / ((237.3 + T_mean) ** 2)
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    gamma = 0.665e-3 * P

    # Calculate ETP
    numerator = 0.408 * delta * Rg_net + gamma * (900 / (T_mean + 273)) * u_2 * (es - ea)
    denominator = delta + gamma * (1 + 0.34 * u_2)
    ETP = numerator / denominator

    return ETP

def get_solar_radiation_and_etp(latitude, longitude, zipcode, country, target_date):
    target_date = datetime.strptime(target_date, "%Y%m%d").date()
    
    # Get solar radiation
    solar_radiation = get_solar_radiation(latitude, longitude, target_date.strftime("%Y%m%d"))
    
    # Get weather data
    start_date = target_date - timedelta(days=1)  # Get an extra day to ensure we have full data for the target date
    end_date = target_date + timedelta(days=1)
    weather_data = get_weather_data(zipcode, country, start_date, end_date)
    
    if weather_data.empty or solar_radiation is None:
        return None, None
    
    # Preprocess weather data
    daily_weather_data = preprocess_weather_data(weather_data)
    
    # Get the data for the target date
    target_weather_data = daily_weather_data.loc[target_date]
    
    if target_weather_data.empty:
        return None, None
    
    # Calculate ETP
    etp = calculate_etp(target_weather_data, solar_radiation)
    
    return solar_radiation, etp

# Test functions
def test_preprocess_weather_data():
    # Create sample weather data
    date_range = pd.date_range(start='2024-05-01', end='2024-05-03', freq='H')
    test_data = pd.DataFrame({
        'timestamp': date_range,
        'temperature': np.random.uniform(15, 25, len(date_range)),
        'relativeHumidity': np.random.uniform(40, 80, len(date_range)),
        'windSpeed': np.random.uniform(0, 10, len(date_range))
    })
    
    processed_data = preprocess_weather_data(test_data)
    
    assert len(processed_data) == 3, "Should have 3 days of data"
    assert all(col in processed_data.columns for col in ['temperature_mean', 'temperature_min', 'temperature_max', 'relativeHumidity_mean', 'windSpeed_mean']), "Missing expected columns"

def test_calculate_etp():
    weather_data = pd.Series({
        'temperature_mean': 20,
        'temperature_min': 15,
        'temperature_max': 25,
        'relativeHumidity_mean': 60,
        'windSpeed_mean': 5
    })
    solar_radiation = 20  # MJ/m²/day

    etp = calculate_etp(weather_data, solar_radiation)
    assert etp > 0, "ETP should be positive"

def test_get_solar_radiation_and_etp():
    # Mock the get_solar_radiation function
    global get_solar_radiation
    original_get_solar_radiation = get_solar_radiation
    get_solar_radiation = lambda lat, lon, date: 20  # Mock function always returns 20 MJ/m²/day

    latitude = 40.7128
    longitude = -74.0060
    zipcode = "10001"
    country = "US"
    target_date = "20240510"

    solar_radiation, etp = get_solar_radiation_and_etp(latitude, longitude, zipcode, country, target_date)

    assert solar_radiation is not None, "Solar radiation should not be None"
    assert etp is not None, "ETP should not be None"
    assert solar_radiation == 20, "Solar radiation should be 20 MJ/m²/day"
    assert etp > 0, "ETP should be positive"

    # Restore the original function
    get_solar_radiation = original_get_solar_radiation

# Run try one call
if __name__ == "__main__":
    print("Running tests...")
    test_preprocess_weather_data()
    test_calculate_etp()
    test_get_solar_radiation_and_etp()
    print("All tests passed!")

    print("\nRunning example calculation...")
    latitude = 40.7128
    longitude = -74.0060
    zipcode = "10001"
    country = "US"
    target_date = "20240510"
    
    solar_radiation, etp = get_solar_radiation_and_etp(latitude, longitude, zipcode, country, target_date)
    
    if solar_radiation is not None and etp is not None:
        print(f"Solar Radiation: {solar_radiation:.2f} MJ/m²/day")
        print(f"Evapotranspiration: {etp:.2f} mm/day")
    else:
        print("Unable to calculate solar radiation and evapotranspiration for the given date.")
