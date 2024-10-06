# /home/hagamaya/Desktop/NasaSpaceApp24/run_growth_potential.py

import sys
import os
import argparse

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from GrowthIndicators.handle_growth_potential import get_growth_potential24h, get_growth_potential_day

def main():
    parser = argparse.ArgumentParser(description='Calculate growth potential for plants.')
    parser.add_argument('function', choices=['24h', 'day'], help='Choose between 24-hour or daily growth potential')
    parser.add_argument('zipcode', help='Zipcode of the location')
    parser.add_argument('country', help='Country code (e.g., US)')
    parser.add_argument('date', help='Date in YYYY-MM-DD format')
    parser.add_argument('plant_type', choices=['C3', 'C4'], help='Plant type (C3 or C4)')

    args = parser.parse_args()

    if args.function == '24h':
        result = get_growth_potential24h(args.zipcode, args.country, args.date, args.plant_type)
    else:
        result = get_growth_potential_day(args.zipcode, args.country, args.date, args.plant_type)

    print(result)

if __name__ == "__main__":
    main()