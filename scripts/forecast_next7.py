#!/usr/bin/env python3
"""
Step 4: Generate 7-day forecast using trained model
使用训练好的LR模型 + 气候学 + 天文潮汐 → 生成未来7天预测
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
import joblib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_FILE = os.path.join(ROOT, "models", "biolum_lr.pkl")
CLIM_FILE = os.path.join(ROOT, "data", "climatology.json")
ASTRO_FILE = os.path.join(ROOT, "data", "astronomy_next7.json")
OUTPUT_FILE = os.path.join(ROOT, "site", "forecast.json")

def load_model():
    """加载训练好的模型"""
    model_data = joblib.load(MODEL_FILE)
    return model_data['model'], model_data['feature_cols']

def load_climatology():
    """加载气候学数据"""
    with open(CLIM_FILE, 'r') as f:
        return json.load(f)

def load_astronomy():
    """加载天文数据"""
    with open(ASTRO_FILE, 'r') as f:
        return json.load(f)

def extract_features(astro_day, clim):
    """
    从天文数据和气候学数据提取特征
    """
    date = datetime.fromisoformat(astro_day['date'])
    doy = date.timetuple().tm_yday
    
    # 天文特征
    moon_illum = astro_day['moon']['illumination']
    is_dark_night = astro_day['moon']['is_dark_night']
    tide_level = astro_day['tide']['current_level']
    near_low_tide = astro_day['tide']['near_low_tide']
    
    # 气候学特征
    wave_height = float(clim['wave_height_doy'].get(str(doy), 1.0))
    water_temp = float(clim['water_temp_doy'].get(str(doy), 16.0))
    season_sin = np.sin(2 * np.pi * doy / 365)
    
    # 构建特征向量 (与训练时一致)
    features = {
        'moon_illumination': moon_illum,
        'is_night': 1,  # 预测夜间情况 (生物发光主要在夜间)
        'tide_level': tide_level,
        'wave_height': wave_height,
        'water_temp': water_temp,
        'season_sin': season_sin
    }
    
    return features

def predict_for_day(model, feature_cols, features):
    """对单天进行预测"""
    X = np.array([[features[col] for col in feature_cols]])
    
    # 预测概率
    prob = model.predict_proba(X)[0, 1]  # 类别1(高可能)的概率
    
    # 转换为0-100的评分
    score = int(prob * 100)
    
    # 评级
    if score >= 70:
        rating = "Excellent"
        icon = "🌟"
    elif score >= 50:
        rating = "Good"
        icon = "✨"
    elif score >= 30:
        rating = "Fair"
        icon = "💫"
    else:
        rating = "Poor"
        icon = "⭐"
    
    return {
        'score': score,
        'rating': rating,
        'icon': icon,
        'probability': round(prob, 3)
    }

def generate_forecast():
    """生成7天预测"""
    print("=" * 60)
    print("🔮 BlueGlow - Step 4: Generate 7-Day Forecast")
    print("=" * 60)
    
    # 1. 加载模型和数据
    print("\n📦 Loading model and data...")
    model, feature_cols = load_model()
    clim = load_climatology()
    astro = load_astronomy()
    
    print(f"   Model: {MODEL_FILE}")
    print(f"   Features: {', '.join(feature_cols)}")
    
    # 2. 对每天进行预测
    print("\n🔮 Generating predictions...")
    forecasts = []
    
    for day in astro['forecast_days']:
        date = datetime.fromisoformat(day['date'])
        
        # 提取特征
        features = extract_features(day, clim)
        
        # 预测
        pred = predict_for_day(model, feature_cols, features)
        
        # 构建预测结果
        forecast = {
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),
            'score': pred['score'],
            'rating': pred['rating'],
            'conditions': {
                'moon': {
                    'phase': day['moon']['phase_name'],
                    'illumination': day['moon']['illumination'],
                    'dark_night': day['moon']['is_dark_night']
                },
                'tide': {
                    'level': day['tide']['current_level'],
                    'near_low_tide': day['tide']['near_low_tide'],
                    'low_tide_times': day['tide']['low_tide_times'][:2]
                },
                'wave_height_m': round(features['wave_height'], 2),
                'water_temp_c': round(features['water_temp'], 1)
            },
            'recommendation': generate_recommendation(pred['score'], day)
        }
        
        forecasts.append(forecast)
        
        # 打印预测
        print(f"   {date.strftime('%Y-%m-%d %a')} | Score: {pred['score']:3d}/100 {pred['icon']} | {pred['rating']:10s} | Moon: {day['moon']['illumination']:.2f}")
    
    # 3. 保存预测结果
    output = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'location': {
            'name': 'La Jolla Shores (Scripps Nearshore)',
            'lat': astro['location']['lat'],
            'lon': astro['location']['lon']
        },
        'model_version': '1.0-climatology',
        'forecasts': forecasts,
        'metadata': {
            'note': 'Forecast based on climatology + astronomy. Will improve with real-time SST/Chl-a data.',
            'features_used': feature_cols,
            'weak_supervision': True
        }
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Forecast saved: {OUTPUT_FILE}")
    print(f"   Size: {os.path.getsize(OUTPUT_FILE)} bytes")
    print("\n" + "=" * 60)
    print("✅ Forecast generation complete!")
    print("   Next: Open site/index.html to view the forecast")
    print("=" * 60)

def generate_recommendation(score, day):
    """生成观测建议"""
    if score >= 70:
        return f"Excellent conditions! Best viewing during low tide at {day['tide']['low_tide_times'][0] if day['tide']['low_tide_times'] else 'evening'}."
    elif score >= 50:
        return "Good conditions for bioluminescence viewing. Try visiting during low tide."
    elif score >= 30:
        return "Fair conditions. May see some bioluminescence, but not guaranteed."
    else:
        moon_too_bright = day['moon']['illumination'] > 0.5
        if moon_too_bright:
            return "Poor conditions due to bright moonlight. Try a darker night."
        else:
            return "Conditions are not ideal. Check back in a few days."

if __name__ == "__main__":
    generate_forecast()
