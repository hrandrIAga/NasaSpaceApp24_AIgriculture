# /home/hagamaya/Desktop/NasaSpaceApp24/run_gdd.py
import sys
import os
import argparse

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from GrowthIndicators.handle_gdd import get_gdd_daily, get_gdd_cumulative

def main():
    parser = argparse.ArgumentParser(description='Calculate Growing Degree Days (GDD) for plants.')
    parser.add_argument('function', choices=['daily', 'cumulative'], help='Choose between daily or cumulative GDD calculation')
    parser.add_argument('zipcode', help='Zipcode of the location')
    parser.add_argument('country', help='Country code (e.g., US)')
    parser.add_argument('date', help='Date in YYYY-MM-DD format')
    parser.add_argument('plant_type', choices=['C3', 'C4'], help='Plant type (C3 or C4)')

    args = parser.parse_args()

    if args.function == 'daily':
        result = get_gdd_daily(args.zipcode, args.country, args.date, args.plant_type)
    else:  # cumulative
        result = get_gdd_cumulative(args.zipcode, args.country, args.date, args.plant_type)

    print(result)

if __name__ == "__main__":
    main()