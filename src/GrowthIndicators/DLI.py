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
from statsmodels.tsa.statespace.sarimax import SARIMAX

def get_solar_radiation(start_date, end_date, latitude, longitude):
    """
    Obtient les données de radiation solaire en utilisant SARIMAX pour les prédictions.
    Cette fonction devrait être remplacée par votre implémentation réelle de SARIMAX.
    """
    # Simulation de données pour cet exemple
    date_range = pd.date_range(start=start_date, end=end_date)
    radiation_data = pd.Series(np.random.uniform(10, 20, len(date_range)), index=date_range)
    return radiation_data

def calculate_dli(radiation_data, latitude, date):
    """
    Calcule le Daily Light Integral (DLI) à partir des données de radiation solaire.
    
    :param radiation_data: Série pandas contenant les données de radiation solaire en MJ/m²/jour
    :param latitude: Latitude du lieu en degrés
    :param date: Date pour laquelle calculer le DLI
    :return: DLI en mol/m²/jour
    """
    # Conversion de MJ/m²/jour en µmol/m²/s
    # Facteur de conversion approximatif : 1 W/m² = 2.02 µmol/m²/s
    # 1 MJ/m²/jour = 11.57 W/m² en moyenne sur 24 heures
    umol_per_s = radiation_data * 11.57 * 2.02
    
    # Calcul de la durée du jour
    day_of_year = date.timetuple().tm_yday
    declination = 23.45 * np.sin(np.radians((360/365) * (day_of_year - 81)))
    lat_rad = np.radians(latitude)
    day_length = 24 - (24/np.pi) * np.arccos(
        (np.sin(np.radians(-0.83)) + np.sin(lat_rad) * np.sin(np.radians(declination))) / 
        (np.cos(lat_rad) * np.cos(np.radians(declination)))
    )
    
    # Calcul du DLI
    dli = umol_per_s * day_length * 3600 / 1e6  # Conversion en mol/m²/jour
    
    return dli

def main(zipcode, country, start_date, end_date, latitude, longitude):
    # Obtenir les données météorologiques
    weather_data = get_weather_data(zipcode, country, start_date, end_date)
    
    # Convertir en DataFrame pandas
    df = pd.DataFrame(weather_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Obtenir les données de radiation solaire
    radiation_data = get_solar_radiation(start_date, end_date, latitude, longitude)
    df['radiation'] = radiation_data
    
    # Calculer le DLI pour chaque jour
    df['dli'] = df.apply(lambda row: calculate_dli(row['radiation'], latitude, row.name), axis=1)
    
    # Afficher les résultats
    print(df[['radiation', 'dli']])

if __name__ == "__main__":
    # Exemple d'utilisation
    zipcode = "75001"  # Code postal de Paris
    country = "FR"
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    latitude = 48.8566  # Latitude de Paris
    longitude = 2.3522  # Longitude de Paris
    
    main(zipcode, country, start_date, end_date, latitude, longitude)