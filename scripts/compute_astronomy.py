#!/usr/bin/env python3
"""
计算天文和潮汐特征 - 本地计算，不依赖网络
月相、月照度、潮汐时间（基于天文潮汐理论）
"""

import os
import json
import math
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase
from dotenv import dotenv_values

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = {**dotenv_values(os.path.join(ROOT, "config", ".env"))}

# Scripps/La Jolla 坐标
LAT = float(CFG.get("LAT_MIN", 32.86))
LON = float(CFG.get("LON_MIN", -117.26))
LOCATION = LocationInfo("La Jolla", "USA", "America/Los_Angeles", LAT, LON)

def moon_illumination(date):
    """
    计算月照度 (0-1)
    0 = 新月(暗), 1 = 满月(亮)
    """
    # astral.moon.phase 返回月相角度 (0-28天周期)
    moon_phase_value = phase(date)
    # 转换为照度: 满月在phase=14附近
    illumination = 1.0 - abs(moon_phase_value - 14) / 14.0
    return max(0.0, min(1.0, illumination))

def is_dark_night(date):
    """
    判断是否为暗夜 (低月照 < 0.3)
    适合观测生物发光的条件
    """
    illum = moon_illumination(date)
    return illum < 0.3

def compute_tides(date):
    """
    简化天文潮汐计算
    使用 M2 主太阴半日潮 周期 (12.42小时)
    
    返回: {
        "high_tide_times": [datetime, ...],
        "low_tide_times": [datetime, ...],
        "current_level": float  # -1.0 (低潮) 至 1.0 (高潮)
    }
    """
    # M2潮汐周期 (12小时25分钟)
    M2_PERIOD_HOURS = 12.42
    
    # 参考时间: 2024-01-01 00:00 UTC 为高潮
    # (这是简化假设，实际需要调和常数)
    reference = datetime(2024, 1, 1, 0, 0)
    hours_since_ref = (date - reference).total_seconds() / 3600
    
    # M2相位 (0-2π)
    phase_m2 = (hours_since_ref / M2_PERIOD_HOURS) * 2 * math.pi
    
    # 潮位 (-1 至 1)
    tide_level = math.cos(phase_m2)
    
    # 计算当天的高低潮时间
    day_start = datetime(date.year, date.month, date.day, 0, 0)
    tide_times = {"high": [], "low": []}
    
    for hour_offset in range(0, 26):  # 24小时+余量
        t = day_start + timedelta(hours=hour_offset * M2_PERIOD_HOURS / 2)
        if t.day != date.day:
            continue
        
        hrs = (t - reference).total_seconds() / 3600
        phase = (hrs / M2_PERIOD_HOURS) * 2 * math.pi
        level = math.cos(phase)
        
        if hour_offset % 2 == 0:
            tide_times["high"].append(t.isoformat())
        else:
            tide_times["low"].append(t.isoformat())
    
    return {
        "high_tide_times": tide_times["high"][:2],  # 每天约2次高潮
        "low_tide_times": tide_times["low"][:2],     # 每天约2次低潮
        "current_level": float(tide_level)
    }

def is_near_low_tide(date, window_hours=2):
    """
    判断是否在低潮前后±window_hours时间内
    """
    tides = compute_tides(date)
    
    for low_time_str in tides["low_tide_times"]:
        low_time = datetime.fromisoformat(low_time_str)
        diff = abs((date - low_time).total_seconds() / 3600)
        if diff <= window_hours:
            return True
    
    return False

def compute_astronomy_features(date):
    """
    计算单个日期的所有天文特征
    """
    s = sun(LOCATION.observer, date=date)
    
    moon_illum = moon_illumination(date)
    dark_night = is_dark_night(date)
    tides = compute_tides(date)
    near_low_tide = is_near_low_tide(date, window_hours=2)
    
    return {
        "date": date.isoformat(),
        "sun": {
            "sunrise": s["sunrise"].isoformat(),
            "sunset": s["sunset"].isoformat(),
            "noon": s["noon"].isoformat()
        },
        "moon": {
            "illumination": round(moon_illum, 3),
            "phase_name": get_moon_phase_name(moon_illumination(date)),
            "is_dark_night": dark_night
        },
        "tide": {
            "high_tide_times": tides["high_tide_times"],
            "low_tide_times": tides["low_tide_times"],
            "current_level": round(tides["current_level"], 3),
            "near_low_tide": near_low_tide
        }
    }

def get_moon_phase_name(illumination):
    """月相名称"""
    if illumination < 0.1:
        return "New Moon"
    elif illumination < 0.4:
        return "Crescent"
    elif illumination < 0.6:
        return "Quarter"
    elif illumination < 0.9:
        return "Gibbous"
    else:
        return "Full Moon"

def compute_next_n_days(n=7):
    """计算未来N天的天文特征"""
    today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    
    features = []
    for i in range(n):
        date = today + timedelta(days=i)
        feat = compute_astronomy_features(date)
        features.append(feat)
    
    return features

def main():
    print("=" * 60)
    print("🌙 BlueGlow - Compute Astronomy & Tides")
    print("=" * 60)
    print(f"📍 Location: {LOCATION.name} ({LAT:.4f}, {LON:.4f})")
    
    # 计算未来7天
    print("\n🔮 Computing next 7 days...")
    features = compute_next_n_days(7)
    
    print("\n📊 Summary:")
    for feat in features:
        date = datetime.fromisoformat(feat["date"])
        moon_illum = feat["moon"]["illumination"]
        dark = "🌑" if feat["moon"]["is_dark_night"] else "🌕"
        tide = "🌊" if feat["tide"]["near_low_tide"] else "〰️"
        
        print(f"  {date.strftime('%Y-%m-%d')} | Moon: {moon_illum:.2f} {dark} | {tide} Low tide ±2h")
    
    # 保存
    output_file = os.path.join(ROOT, "data", "astronomy_next7.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    output = {
        "location": {
            "name": LOCATION.name,
            "lat": LAT,
            "lon": LON
        },
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "forecast_days": features
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Astronomy data saved: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
