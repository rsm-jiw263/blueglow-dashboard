#!/usr/bin/env python3
"""
生成每3小时的详细预测 (每天8个时段)
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
import joblib
from compute_astronomy import moon_illumination, compute_tides, is_near_low_tide, LOCATION, LAT, LON
from astral.sun import sun

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_FILE = os.path.join(ROOT, "models", "biolum_lr.pkl")
CLIM_FILE = os.path.join(ROOT, "data", "climatology.json")
OUTPUT_FILE = os.path.join(ROOT, "site", "forecast_detailed.json")

def load_model():
    model_data = joblib.load(MODEL_FILE)
    return model_data['model'], model_data['feature_cols']

def load_climatology():
    with open(CLIM_FILE, 'r') as f:
        return json.load(f)

def predict_timeslot(model, feature_cols, dt, clim):
    """预测特定时刻的评分"""
    doy = dt.timetuple().tm_yday
    hour = dt.hour
    
    # 月照度
    moon_illum = moon_illumination(dt)
    
    # 是否夜间 (日落后到日出前)
    s = sun(LOCATION.observer, date=dt.date())
    # 转换为naive datetime进行比较
    sunrise_naive = s['sunrise'].replace(tzinfo=None)
    sunset_naive = s['sunset'].replace(tzinfo=None)
    is_night = (dt < sunrise_naive or dt > sunset_naive)
    
    # 潮汐
    tides = compute_tides(dt)
    tide_level = tides['current_level']
    near_low = is_near_low_tide(dt, window_hours=2)
    
    # 气候学特征
    wave_height = float(clim['wave_height_doy'].get(str(doy), 1.0))
    water_temp = float(clim['water_temp_doy'].get(str(doy), 16.0))
    season_sin = np.sin(2 * np.pi * doy / 365)
    
    # 构建特征
    features = {
        'moon_illumination': moon_illum,
        'is_night': int(is_night),
        'tide_level': tide_level,
        'wave_height': wave_height,
        'water_temp': water_temp,
        'season_sin': season_sin
    }
    
    X = np.array([[features[col] for col in feature_cols]])
    prob = model.predict_proba(X)[0, 1]
    score = int(prob * 100)
    
    return {
        'score': score,
        'probability': round(prob, 3),
        'features': features,
        'is_night': is_night,
        'near_low_tide': near_low
    }

def generate_daily_timeslots(date, model, feature_cols, clim):
    """为某一天生成8个时段（3小时间隔）的预测"""
    timeslots = []
    
    # 0:00, 3:00, 6:00, 9:00, 12:00, 15:00, 18:00, 21:00
    for hour in range(0, 24, 3):
        dt = datetime(date.year, date.month, date.day, hour, 0, 0)
        pred = predict_timeslot(model, feature_cols, dt, clim)
        
        # 评级
        score = pred['score']
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
        
        timeslot = {
            'time': dt.strftime('%H:%M'),
            'datetime': dt.isoformat(),
            'score': score,
            'rating': rating,
            'icon': icon,
            'is_night': pred['is_night'],
            'conditions': {
                'moon_illumination': round(pred['features']['moon_illumination'], 3),
                'tide_level': round(pred['features']['tide_level'], 3),
                'near_low_tide': pred['near_low_tide'],
                'wave_height_m': round(pred['features']['wave_height'], 2),
                'water_temp_c': round(pred['features']['water_temp'], 1)
            }
        }
        
        timeslots.append(timeslot)
    
    return timeslots

def find_best_week_with_timeslots(days_to_check=30):
    """寻找最佳周并生成详细时段预测"""
    print(f"🔍 搜索未来{days_to_check}天的最佳观测周（含3小时时段详情）...")
    
    model, feature_cols = load_model()
    clim = load_climatology()
    
    # 先找到最佳周的起始日期
    today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    daily_scores = []
    
    for i in range(days_to_check):
        date = today + timedelta(days=i)
        # 计算当天所有时段的平均分
        timeslots = generate_daily_timeslots(date, model, feature_cols, clim)
        avg_score = sum(t['score'] for t in timeslots) / len(timeslots)
        daily_scores.append((date, avg_score))
    
    # 找到连续7天平均分最高的窗口
    best_avg = -1
    best_start_idx = 0
    
    for i in range(len(daily_scores) - 6):
        week_avg = sum(daily_scores[i+j][1] for j in range(7)) / 7
        if week_avg > best_avg:
            best_avg = week_avg
            best_start_idx = i
    
    best_week_start = daily_scores[best_start_idx][0]
    print(f"\n✅ 找到最佳观测周:")
    print(f"   起始日期: {best_week_start.strftime('%Y-%m-%d')}")
    print(f"   平均评分: {best_avg:.1f}/100")
    
    # 为最佳周的7天生成详细时段
    forecasts = []
    for i in range(7):
        date = best_week_start + timedelta(days=i)
        timeslots = generate_daily_timeslots(date, model, feature_cols, clim)
        
        # 计算当天最佳时段
        best_timeslot = max(timeslots, key=lambda t: t['score'])
        avg_score = int(sum(t['score'] for t in timeslots) / len(timeslots))
        
        # 生成建议
        night_slots = [t for t in timeslots if t['is_night']]
        if night_slots:
            best_night = max(night_slots, key=lambda t: t['score'])
            if best_night['score'] >= 70:
                recommendation = f"最佳时段: {best_night['time']} (评分{best_night['score']}), 夜间低潮窗口"
            elif best_night['score'] >= 50:
                recommendation = f"推荐时段: {best_night['time']} (评分{best_night['score']})"
            else:
                recommendation = "今日条件一般，建议选择其他日期"
        else:
            recommendation = "无夜间时段数据"
        
        forecast = {
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),
            'avg_score': avg_score,
            'best_score': best_timeslot['score'],
            'best_time': best_timeslot['time'],
            'timeslots': timeslots,
            'recommendation': recommendation
        }
        
        forecasts.append(forecast)
        
        print(f"   {date.strftime('%m-%d %a')}: 平均{avg_score:3d}分 | 最高{best_timeslot['score']:3d}分@{best_timeslot['time']}")
    
    return forecasts

def main():
    print("=" * 60)
    print("🔮 BlueGlow - Detailed 3-Hour Forecast")
    print("=" * 60)
    
    # 生成详细预测
    forecasts = find_best_week_with_timeslots(days_to_check=30)
    
    # 保存
    output = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'location': {
            'name': 'La Jolla Shores (Scripps Nearshore)',
            'lat': LAT,
            'lon': LON
        },
        'model_version': '1.0-climatology',
        'forecast_type': '3-hour intervals (8 timeslots per day)',
        'forecasts': forecasts,
        'metadata': {
            'search_window': '30 days',
            'timeslot_interval': '3 hours',
            'timeslots_per_day': 8,
            'selection_method': 'Highest average score for 7 consecutive days'
        }
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Detailed forecast saved: {OUTPUT_FILE}")
    print(f"   Size: {os.path.getsize(OUTPUT_FILE)} bytes")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
