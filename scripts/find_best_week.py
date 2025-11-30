#!/usr/bin/env python3
"""
寻找未来30天内评分最高的7天连续时段
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
import joblib
from compute_astronomy import compute_astronomy_features, LOCATION, LAT, LON

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_FILE = os.path.join(ROOT, "models", "biolum_lr.pkl")
CLIM_FILE = os.path.join(ROOT, "data", "climatology.json")
OUTPUT_FILE = os.path.join(ROOT, "site", "forecast.json")

def load_model():
    model_data = joblib.load(MODEL_FILE)
    return model_data['model'], model_data['feature_cols']

def load_climatology():
    with open(CLIM_FILE, 'r') as f:
        return json.load(f)

def predict_single_day(model, feature_cols, date, clim):
    """预测单日评分"""
    doy = date.timetuple().tm_yday
    
    # 计算天文特征
    astro = compute_astronomy_features(date)
    
    # 提取特征
    features = {
        'moon_illumination': astro['moon']['illumination'],
        'is_night': 1,
        'tide_level': astro['tide']['current_level'],
        'wave_height': float(clim['wave_height_doy'].get(str(doy), 1.0)),
        'water_temp': float(clim['water_temp_doy'].get(str(doy), 16.0)),
        'season_sin': np.sin(2 * np.pi * doy / 365)
    }
    
    X = np.array([[features[col] for col in feature_cols]])
    prob = model.predict_proba(X)[0, 1]
    score = int(prob * 100)
    
    return score, astro, features

def find_best_week(days_to_check=30):
    """在未来N天中寻找评分最高的连续7天"""
    print(f"🔍 搜索未来{days_to_check}天，寻找最佳观测周...")
    
    model, feature_cols = load_model()
    clim = load_climatology()
    
    # 计算所有日期的评分
    today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    all_predictions = []
    
    for i in range(days_to_check):
        date = today + timedelta(days=i)
        score, astro, features = predict_single_day(model, feature_cols, date, clim)
        
        all_predictions.append({
            'date': date,
            'score': score,
            'astro': astro,
            'features': features
        })
    
    # 找到连续7天平均分最高的窗口
    best_avg = -1
    best_start_idx = 0
    
    for i in range(len(all_predictions) - 6):
        week_scores = [all_predictions[i+j]['score'] for j in range(7)]
        avg_score = sum(week_scores) / 7
        
        if avg_score > best_avg:
            best_avg = avg_score
            best_start_idx = i
    
    print(f"\n✅ 找到最佳观测周:")
    print(f"   起始日期: {all_predictions[best_start_idx]['date'].strftime('%Y-%m-%d')}")
    print(f"   平均评分: {best_avg:.1f}/100")
    
    best_week = all_predictions[best_start_idx:best_start_idx+7]
    
    print(f"\n📊 该周详细评分:")
    for pred in best_week:
        date = pred['date']
        print(f"   {date.strftime('%m-%d %a')}: {pred['score']:3d}分 | 月照:{pred['astro']['moon']['illumination']:.2f}")
    
    return best_week

def generate_forecast_from_predictions(predictions):
    """从预测结果生成forecast.json"""
    forecasts = []
    
    for pred in predictions:
        date = pred['date']
        score = pred['score']
        astro = pred['astro']
        features = pred['features']
        
        # 评级
        if score >= 70:
            rating = "Excellent"
        elif score >= 50:
            rating = "Good"
        elif score >= 30:
            rating = "Fair"
        else:
            rating = "Poor"
        
        # 建议
        if score >= 70:
            low_times = astro['tide']['low_tide_times']
            time_str = low_times[0] if low_times else 'evening'
            recommendation = f"Excellent conditions! Best viewing during low tide at {time_str}."
        elif score >= 50:
            recommendation = "Good conditions for bioluminescence viewing. Try visiting during low tide."
        elif score >= 30:
            recommendation = "Fair conditions. May see some bioluminescence, but not guaranteed."
        else:
            moon_too_bright = astro['moon']['illumination'] > 0.5
            if moon_too_bright:
                recommendation = "Poor conditions due to bright moonlight. Try a darker night."
            else:
                recommendation = "Conditions are not ideal. Check back in a few days."
        
        forecast = {
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),
            'score': score,
            'rating': rating,
            'conditions': {
                'moon': {
                    'phase': astro['moon']['phase_name'],
                    'illumination': astro['moon']['illumination'],
                    'dark_night': astro['moon']['is_dark_night']
                },
                'tide': {
                    'level': astro['tide']['current_level'],
                    'near_low_tide': astro['tide']['near_low_tide'],
                    'low_tide_times': astro['tide']['low_tide_times'][:2]
                },
                'wave_height_m': round(features['wave_height'], 2),
                'water_temp_c': round(features['water_temp'], 1)
            },
            'recommendation': recommendation
        }
        
        forecasts.append(forecast)
    
    return forecasts

def main():
    print("=" * 60)
    print("🔮 BlueGlow - Find Best Week")
    print("=" * 60)
    
    # 寻找最佳周
    best_week = find_best_week(days_to_check=30)
    
    # 生成预测
    forecasts = generate_forecast_from_predictions(best_week)
    
    # 保存
    output = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'location': {
            'name': 'La Jolla Shores (Scripps Nearshore)',
            'lat': LAT,
            'lon': LON
        },
        'model_version': '1.0-climatology',
        'note': 'Best 7-day window selected from next 30 days',
        'forecasts': forecasts,
        'metadata': {
            'search_window': '30 days',
            'selection_method': 'Highest average score for 7 consecutive days',
            'features_used': ['moon_illumination', 'is_night', 'tide_level', 'wave_height', 'water_temp', 'season_sin'],
            'weak_supervision': True
        }
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Forecast saved: {OUTPUT_FILE}")
    print(f"   Size: {os.path.getsize(OUTPUT_FILE)} bytes")
    print("\n" + "=" * 60)
    print("✅ Best week forecast generated!")
    print("   Refresh browser to see the improved predictions")
    print("=" * 60)

if __name__ == "__main__":
    main()
