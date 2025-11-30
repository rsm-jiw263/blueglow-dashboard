#!/usr/bin/env python3
"""
生成一整年(365天)的预测数据,支持离线查询
"""

import os
import json
import sys
from datetime import datetime, timedelta
from forecast_detailed import (
    load_model, load_climatology, generate_daily_timeslots,
    LAT, LON
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FILE = os.path.join(ROOT, "site", "forecast_year.json")

def main():
    print("=" * 60)
    print("🌊 Generating 1-Year Bioluminescence Forecast Data")
    print("=" * 60)
    
    # 加载模型和气候学数据
    print("\n📦 Loading model and climatology...")
    model, feature_cols = load_model()
    clim = load_climatology()
    print("✓ Model and climatology loaded")
    
    # 生成从今天开始的365天数据
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=365)
    
    print(f"\n📅 Generating forecasts from {start_date} to {end_date}")
    print(f"   Total days: 365")
    
    all_forecasts = []
    current_date = start_date
    day_count = 0
    
    while current_date < end_date:
        day_count += 1
        
        if day_count % 30 == 0 or day_count == 1:
            print(f"   Processing day {day_count}/365: {current_date}")
        
        # 生成该天的所有时段预测
        timeslots = generate_daily_timeslots(current_date, model, feature_cols, clim)
        
        # 计算平均分和最佳时段
        scores = [ts['score'] for ts in timeslots]
        avg_score = int(sum(scores) / len(scores))
        best_score = max(scores)
        best_timeslot = timeslots[scores.index(best_score)]
        
        forecast = {
            'date': current_date.strftime('%Y-%m-%d'),
            'day_of_week': current_date.strftime('%A'),
            'avg_score': avg_score,
            'best_score': best_score,
            'best_time': best_timeslot['time'],
            'timeslots': timeslots
        }
        
        all_forecasts.append(forecast)
        current_date += timedelta(days=1)
    
    # 构建完整输出
    output_data = {
        'generated_at': datetime.now().isoformat() + 'Z',
        'location': {
            'name': 'La Jolla Shores (Scripps Nearshore)',
            'lat': LAT,
            'lon': LON
        },
        'model_version': '1.0-climatology',
        'forecast_type': '3-hour intervals (8 timeslots per day)',
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': (end_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'total_days': len(all_forecasts)
        },
        'forecasts': all_forecasts
    }
    
    # 保存到文件
    print(f"\n💾 Saving to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"✓ Saved {len(all_forecasts)} days of forecasts")
    print(f"✓ File size: {file_size_mb:.2f} MB")
    
    # 统计信息
    print("\n📊 Statistics:")
    all_scores = [f['avg_score'] for f in all_forecasts]
    print(f"   Average score across all days: {sum(all_scores)/len(all_scores):.1f}")
    print(f"   Best day: {max(all_forecasts, key=lambda x: x['best_score'])['date']} "
          f"(score: {max(f['best_score'] for f in all_forecasts)})")
    print(f"   Worst day: {min(all_forecasts, key=lambda x: x['avg_score'])['date']} "
          f"(score: {min(f['avg_score'] for f in all_forecasts)})")
    
    print("\n✅ Generation complete!")
    print(f"📂 Output: {OUTPUT_FILE}")
    print("\n💡 You can now query any date offline by loading this file in the frontend.")

if __name__ == '__main__':
    main()
