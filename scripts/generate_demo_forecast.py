#!/usr/bin/env python3
"""
Generate demo forecast data for BlueGlow helper
"""
import json
import os
from datetime import datetime, timedelta
import random


def generate_demo_forecast():
    """Generate demo forecast data for the next 7 days"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    forecast_data = {
        "generated_at": datetime.now().isoformat(),
        "location": "Demo Location",
        "forecast": []
    }
    
    # Generate 7 days of demo data
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        
        # Generate random but realistic values
        blueglow_index = random.uniform(3.0, 9.0)
        cloud_cover = random.uniform(0, 100)
        visibility = random.uniform(5, 50)
        
        # Determine quality based on index
        if blueglow_index >= 7:
            quality = "Excellent"
        elif blueglow_index >= 5:
            quality = "Good"
        elif blueglow_index >= 3:
            quality = "Fair"
        else:
            quality = "Poor"
        
        day_data = {
            "date": date.strftime("%Y-%m-%d"),
            "day_name": date.strftime("%A"),
            "blueglow_index": round(blueglow_index, 1),
            "quality": quality,
            "cloud_cover": round(cloud_cover, 1),
            "visibility": round(visibility, 1),
            "moon_phase": round(random.uniform(0, 100), 1)
        }
        
        forecast_data["forecast"].append(day_data)
    
    # Save to file
    output_file = 'data/forecast.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(forecast_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Demo forecast generated: {output_file}")
    print(f"📅 {len(forecast_data['forecast'])} days of forecast data created")
    
    return forecast_data


if __name__ == "__main__":
    generate_demo_forecast()
