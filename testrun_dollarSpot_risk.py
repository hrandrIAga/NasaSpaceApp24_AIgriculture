# testrun_dollar_spot_risk.py
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the function to test
from Disease.get_dollarSpot_risk import get_dollar_spot_risk

def run_tests():
    # Test case 1: Current date
    zipcode = "77050"
    country = "US"
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Test 1: Current date ({today})")
    risk = get_dollar_spot_risk(zipcode, country, today)
    print(f"Dollar Spot Risk: {risk:.2f}%")
    print()

    # Test case 2: 5 days ago
    five_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    print(f"Test 2: 5 days ago ({five_days_ago})")
    risk = get_dollar_spot_risk(zipcode, country, five_days_ago)
    print(f"Dollar Spot Risk: {risk:.2f}%")
    print()

    # Test case 3: Future date (5 days from now)
   # future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    
    #print(f"Test 3: Future date ({future_date})")
    #risk = get_dollar_spot_risk(zipcode, country, future_date)
    #print(f"Dollar Spot Risk: {risk:.2f}%")
    #print()

    # Test case 4: Different zipcode
    different_zipcode = "90210"
    
    print(f"Test 4: Different zipcode ({different_zipcode})")
    risk = get_dollar_spot_risk(different_zipcode, country, today)
    print(f"Dollar Spot Risk: {risk:.2f}%")
    print()

if __name__ == "__main__":
    run_tests()