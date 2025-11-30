#!/usr/bin/env python3
"""
计算气候学特征 - 从历史NDBC数据提取
Climatology: 风速历年同日中位值, SST/Chl-a季节中位值
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(ROOT, "data", "raw")
OUTPUT_FILE = os.path.join(ROOT, "data", "climatology.json")

def load_ndbc_data():
    """加载所有NDBC CSV文件"""
    files = [f for f in os.listdir(RAW_DIR) if f.startswith("ndbc_") and f.endswith(".csv")]
    if not files:
        print("⚠️  No NDBC data found in data/raw/")
        return pd.DataFrame()
    
    dfs = []
    for f in sorted(files):
        path = os.path.join(RAW_DIR, f)
        try:
            df = pd.read_csv(path)
            # 标准化列名
            df.columns = [c.strip() for c in df.columns]
            dfs.append(df)
            print(f"✅ Loaded {f}: {len(df)} rows")
        except Exception as e:
            print(f"⚠️  Failed to load {f}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    return pd.concat(dfs, ignore_index=True)

def parse_ndbc_datetime(df):
    """解析NDBC时间戳"""
    # NDBC格式: YY, MM, DD, hh, mm
    # YY可能是2位或4位年份
    
    # 清理列名
    df.columns = [c.replace('#', '').strip() for c in df.columns]
    
    # 如果有dt列(已解析的时间戳)，直接使用
    if 'dt' in df.columns:
        df['timestamp'] = pd.to_datetime(df['dt'], errors='coerce')
        return df
    
    # 否则手动构建
    year_col = 'YY' if 'YY' in df.columns else 'YYYY'
    
    # YY列可能是4位年份(2024)或2位(24)
    df['year'] = pd.to_numeric(df[year_col], errors='coerce')
    df.loc[df['year'] < 100, 'year'] = df.loc[df['year'] < 100, 'year'].apply(
        lambda y: 1900 + y if y > 50 else 2000 + y
    )
    
    df['timestamp'] = pd.to_datetime(
        df[['year', 'MM', 'DD', 'hh', 'mm']].rename(columns={
            'year': 'year', 'MM': 'month', 'DD': 'day', 
            'hh': 'hour', 'mm': 'minute'
        }), 
        errors='coerce'
    )
    
    return df

def compute_wind_climatology(df):
    """
    计算风浪的历年同日中位值
    46254站是浪高浮标，无风速数据，改用浪高(WVHT)作为风浪代理指标
    返回: dict[day_of_year] = {median_wave_height, median_water_temp}
    """
    # 提取有效浪高数据 (WVHT列, 99/999标记缺失值)
    result = {}
    
    # 1. 浪高 (Wave Height) - 作为风浪强度指标
    if 'WVHT' in df.columns:
        df['WVHT'] = pd.to_numeric(df['WVHT'], errors='coerce')
        df_wave = df[(df['WVHT'] > 0) & (df['WVHT'] < 20) & (df['WVHT'] != 99.0)].copy()
        
        if len(df_wave) > 0:
            df_wave['doy'] = df_wave['timestamp'].dt.dayofyear
            wave_clim = {}
            for doy in range(1, 367):
                subset = df_wave[df_wave['doy'] == doy]['WVHT']
                if len(subset) > 0:
                    wave_clim[doy] = float(subset.median())
            
            # 填充缺失DOY
            for doy in range(1, 367):
                if doy not in wave_clim:
                    before = max([d for d in wave_clim.keys() if d < doy], default=None)
                    after = min([d for d in wave_clim.keys() if d > doy], default=None)
                    if before and after:
                        wave_clim[doy] = (wave_clim[before] + wave_clim[after]) / 2
                    elif before:
                        wave_clim[doy] = wave_clim[before]
                    elif after:
                        wave_clim[doy] = wave_clim[after]
                    else:
                        wave_clim[doy] = 1.0  # 默认1米
            
            result['wave_height'] = wave_clim
            print(f"✅ Wave height climatology: {len(wave_clim)} days")
            print(f"   Example: DOY 1 = {wave_clim.get(1, 0):.2f}m, DOY 180 = {wave_clim.get(180, 0):.2f}m")
    
    # 2. 水温 (Water Temperature) - 补充SST数据
    if 'WTMP' in df.columns:
        df['WTMP'] = pd.to_numeric(df['WTMP'], errors='coerce')
        df_temp = df[(df['WTMP'] > 5) & (df['WTMP'] < 30) & (df['WTMP'] != 999.0)].copy()
        
        if len(df_temp) > 0:
            df_temp['doy'] = df_temp['timestamp'].dt.dayofyear
            temp_clim = {}
            for doy in range(1, 367):
                subset = df_temp[df_temp['doy'] == doy]['WTMP']
                if len(subset) > 0:
                    temp_clim[doy] = float(subset.median())
            
            # 填充缺失DOY
            for doy in range(1, 367):
                if doy not in temp_clim:
                    before = max([d for d in temp_clim.keys() if d < doy], default=None)
                    after = min([d for d in temp_clim.keys() if d > doy], default=None)
                    if before and after:
                        temp_clim[doy] = (temp_clim[before] + temp_clim[after]) / 2
                    elif before:
                        temp_clim[doy] = temp_clim[before]
                    elif after:
                        temp_clim[doy] = temp_clim[after]
                    else:
                        temp_clim[doy] = 16.0  # 默认16°C
            
            result['water_temp'] = temp_clim
            print(f"✅ Water temp climatology: {len(temp_clim)} days")
            print(f"   Example: DOY 1 = {temp_clim.get(1, 0):.2f}°C, DOY 180 = {temp_clim.get(180, 0):.2f}°C")
    
    return result

def compute_seasonal_defaults():
    """
    季节默认值 (SST/Chl-a)
    春夏秋冬的典型值 - 基于San Diego海域经验
    """
    return {
        "sst": {
            "winter": 15.5,  # Dec-Feb, °C
            "spring": 16.5,  # Mar-May
            "summer": 20.0,  # Jun-Aug
            "fall": 18.5     # Sep-Nov
        },
        "chla": {
            "winter": 0.8,   # mg/m³
            "spring": 1.5,   # 春季藻华高峰
            "summer": 0.5,
            "fall": 0.6
        }
    }

def get_season(month):
    """获取季节"""
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

def main():
    print("=" * 60)
    print("🌊 BlueGlow - Compute Climatology")
    print("=" * 60)
    
    # 1. 加载NDBC数据
    print("\n📊 Loading NDBC historical data...")
    df = load_ndbc_data()
    
    if df.empty:
        print("❌ No data available. Please run Step 2 first.")
        return
    
    # 2. 解析时间戳
    print("\n🕐 Parsing timestamps...")
    df = parse_ndbc_datetime(df)
    df = df.dropna(subset=['timestamp'])
    print(f"✅ Parsed {len(df)} valid records")
    print(f"   Time range: {df['timestamp'].min()} → {df['timestamp'].max()}")
    
    # 3. 计算浪高和水温气候态
    print("\n🌊 Computing wave & temperature climatology (DOY median)...")
    clim_data = compute_wind_climatology(df)
    
    # 4. 季节默认值
    print("\n🌡️  Seasonal defaults (SST/Chl-a)...")
    seasonal = compute_seasonal_defaults()
    print(f"   SST: Winter={seasonal['sst']['winter']}°C, Summer={seasonal['sst']['summer']}°C")
    print(f"   Chl-a: Spring={seasonal['chla']['spring']}mg/m³, Summer={seasonal['chla']['summer']}mg/m³")
    
    # 5. 保存
    climatology = {
        "wave_height_doy": clim_data.get('wave_height', {}),  # DOY 1-366 -> median wave height (m)
        "water_temp_doy": clim_data.get('water_temp', {}),    # DOY 1-366 -> median water temp (°C)
        "seasonal_defaults": seasonal,
        "metadata": {
            "created": datetime.utcnow().isoformat() + "Z",
            "ndbc_records": len(df),
            "ndbc_station": "46254 (Scripps Nearshore - Wave Buoy)",
            "note": "Station 46254 is a wave buoy without anemometer. Using WVHT (wave height) as wind-wave proxy.",
            "time_range": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat()
            }
        }
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(climatology, f, indent=2)
    
    print(f"\n✅ Climatology saved: {OUTPUT_FILE}")
    print(f"   Size: {os.path.getsize(OUTPUT_FILE)} bytes")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
