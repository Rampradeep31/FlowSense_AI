import os
import pandas as pd
import numpy as np

def generate_freight_data():
    np.random.seed(42)
    
    # 1. Configuration
    cities = ["Mumbai", "Pune", "Nashik", "Nagpur", "Kolhapur", "Aurangabad", "Thane", "Solapur", "Amravati", "Jalgaon"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    # Pre-define distances between major pairs to make it consistent, fallback to a sensible distance calculation
    # Base distances
    distance_map = {
        ("Mumbai", "Pune"): 150.0,
        ("Mumbai", "Nashik"): 170.0,
        ("Mumbai", "Nagpur"): 800.0,
        ("Mumbai", "Kolhapur"): 380.0,
        ("Mumbai", "Aurangabad"): 330.0,
        ("Pune", "Nashik"): 210.0,
        ("Pune", "Nagpur"): 710.0,
        ("Pune", "Kolhapur"): 230.0,
        ("Nashik", "Aurangabad"): 190.0,
        ("Nagpur", "Aurangabad"): 480.0
    }
    
    n_samples = 1200
    data = []
    
    for _ in range(n_samples):
        # Pick origin and destination
        org = np.random.choice(cities)
        dest = np.random.choice([c for c in cities if c != org])
        
        # Get distance
        key = (org, dest) if (org, dest) in distance_map else ((dest, org) if (dest, org) in distance_map else None)
        if key:
            dist = distance_map[key] + np.random.normal(0, 5) # add minor GPS variation
        else:
            # Random distance based on index diff to keep it consistent
            idx_diff = abs(cities.index(org) - cities.index(dest))
            dist = idx_diff * 90.0 + np.random.uniform(50, 120)
            
        dist = round(max(50.0, dist), 2)
        
        # Fuel price (e.g. 92.0 to 108.0)
        fuel = round(float(np.random.uniform(92.0, 108.0)), 2)
        
        # Month
        month = np.random.choice(months)
        
        # Calculate freight cost with a formula + noise
        # Base charge = Rs 2000
        # Distance rate = Rs 12 per km
        # Fuel factor = fuel price / 100
        # Seasonal factor: Monsoon (July/August) +15%, Festive (Oct/Nov) +10%
        base = 2000.0
        dist_cost = dist * 14.5
        fuel_multiplier = fuel / 95.0
        
        season_multiplier = 1.0
        if month in ["July", "August"]:
            season_multiplier = 1.18 # heavy rains
        elif month in ["October", "November"]:
            season_multiplier = 1.10 # festive demand surge
        elif month in ["April", "May"]:
            season_multiplier = 0.95 # low demand
            
        # Add random noise (unobserved factors like traffic delay, toll charges, helper charges)
        noise = np.random.normal(0, 300)
        
        cost = (base + dist_cost) * fuel_multiplier * season_multiplier + noise
        cost = round(max(1500.0, cost), 2)
        
        data.append({
            "Origin": org,
            "Destination": dest,
            "Distance": dist,
            "Fuel_Price": fuel,
            "Month": month,
            "Freight_Cost": cost
        })
        
    df = pd.DataFrame(data)
    
    # Ensure datasets folder exists
    os.makedirs("ml/datasets", exist_ok=True)
    df.to_csv("ml/datasets/freight_dataset.csv", index=False)
    print(f"Generated {n_samples} rows in ml/datasets/freight_dataset.csv")

if __name__ == "__main__":
    generate_freight_data()
