#!/usr/bin/env python3
"""
Generate forecast data for every day in the next 3 years
预生成未来3年每一天的预测数据
"""

import json
import pickle
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.compute_astronomy import moon_illumination, is_dark_night, compute_tides, get_moon_phase_name
from scripts.compute_climatology import compute_seasonal_defaults, get_season

# La Jolla location
LAT = 32.83
LON = -117.32

# Load seasonal climatology once
SEASONAL_CLIM = compute_seasonal_defaults()

def load_model():
    """Load trained model"""
    model_path = Path(__file__).parent.parent / 'models' / 'biolum_lr.pkl'
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def predict_day(model, date, hour=12):
    """
    Predict bioluminescence score for a specific date and hour

    Args:
        model: Trained ML model
        date: datetime.date object
        hour: Hour of day (0-23)

    Returns:
        dict: Prediction with score, rating, conditions
    """
    dt = datetime.combine(date, datetime.min.time().replace(hour=hour))

    # Get moon data
    moon_illum = moon_illumination(dt)
    moon_phase_name = get_moon_phase_name(moon_illum)

    # Check if night (simplified - assume 6pm to 6am)
    is_night = hour < 6 or hour >= 18

    # Get tide
    tide_level = compute_tides(dt)

    # Get climatology from seasonal data
    season = get_season(date.month)
    clim = SEASONAL_CLIM[season]
    wave_height = clim['wave_height_m']
    water_temp = clim['water_temp_c']

    # Season encoding
    day_of_year = date.timetuple().tm_yday
    season_sin = np.sin(2 * np.pi * day_of_year / 365.25)
    season_cos = np.cos(2 * np.pi * day_of_year / 365.25)

    # Create feature vector
    features = np.array([[
        moon_illum,
        1 if is_night else 0,
        tide_level,
        wave_height,
        water_temp,
        season_sin
    ]])

    # Predict
    score_raw = model.predict_proba(features)[0][1] * 100
    score = int(np.clip(score_raw, 0, 100))

    # Rating
    if score >= 90:
        rating = "Excellent"
        icon = "🌟"
    elif score >= 80:
        rating = "Good"
        icon = "✨"
    elif score >= 70:
        rating = "Fair"
        icon = "💫"
    else:
        rating = "Poor"
        icon = "⭐"

    return {
        'hour': hour,
        'score': score,
        'rating': rating,
        'icon': icon,
        'is_night': is_night,
        'conditions': {
            'moon_illumination': round(moon_illum, 3),
            'moon_phase': moon_phase_name,
            'tide_level': round(tide_level, 3),
            'wave_height_m': wave_height,
            'water_temp_c': water_temp
        }
    }

def generate_day_forecast(model, date):
    """Generate forecast for one day (8 timeslots, 3-hour intervals)"""
    timeslots = []
    scores = []

    for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
        pred = predict_day(model, date, hour)
        scores.append(pred['score'])

        timeslots.append({
            'time': f"{hour:02d}:00",
            'datetime': datetime.combine(date, datetime.min.time().replace(hour=hour)).isoformat(),
            'score': pred['score'],
            'rating': pred['rating'],
            'icon': pred['icon'],
            'is_night': pred['is_night'],
            'conditions': pred['conditions']
        })

    # Find best timeslot
    best_idx = np.argmax(scores)
    best_slot = timeslots[best_idx]

    # Day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_of_week = day_names[date.weekday()]

    return {
        'date': date.isoformat(),
        'day_of_week': day_of_week,
        'avg_score': int(np.mean(scores)),
        'best_score': best_slot['score'],
        'best_time': best_slot['time'],
        'timeslots': timeslots,
        'recommendation': f"Best viewing at {best_slot['time']} (Score: {best_slot['score']})"
    }

def main():
    print("="*60)
    print("🔮 Generating 3-Year Forecast Database")
    print("="*60)

    # Load model
    print("\n📦 Loading model...")
    model = load_model()
    print("   ✓ Model loaded")

    # Generate forecasts
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=365 * 3)  # 3 years

    print(f"\n📅 Date range: {start_date} to {end_date}")
    print(f"   Total days: {(end_date - start_date).days}")

    all_forecasts = {}

    current_date = start_date
    count = 0

    while current_date <= end_date:
        if count % 100 == 0:
            print(f"   Processing: {current_date} ({count} days completed)")

        # Generate forecast for this day
        forecast = generate_day_forecast(model, current_date)

        # Store by date string
        all_forecasts[current_date.isoformat()] = forecast

        current_date += timedelta(days=1)
        count += 1

    # Save to file
    output_path = Path(__file__).parent.parent / 'site' / 'forecast_database.json'

    database = {
        'generated_at': datetime.now().isoformat() + 'Z',
        'location': {
            'name': 'La Jolla Shores (Scripps Nearshore)',
            'lat': LAT,
            'lon': LON
        },
        'model_version': '1.0-climatology',
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'total_days': count
        },
        'forecasts': all_forecasts
    }

    print(f"\n💾 Saving to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(database, f, indent=2)

    file_size = output_path.stat().st_size
    print(f"   File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")

    print("\n" + "="*60)
    print("✅ Forecast database generation complete!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   Total days: {count}")
    print(f"   Date range: {start_date} to {end_date}")
    print(f"   Database: {output_path}")
    print(f"\n💡 Next: Update frontend to use forecast_database.json")

if __name__ == '__main__':
    main()
