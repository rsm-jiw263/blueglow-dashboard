#!/usr/bin/env python3
"""
下载La Jolla真实环境数据
从NOAA和NDBC获取水温、浪高、风速等数据
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import urllib3

# 禁用SSL警告（仅用于NDBC）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_noaa_data(station="9410230", product="water_temperature",
                       begin_date="20240101", end_date="20241231",
                       output_file=None):
    """
    从NOAA Tides & Currents API下载数据

    Parameters:
    -----------
    station : str
        站点ID (9410230 = La Jolla/Scripps Pier)
    product : str
        数据类型: 'water_temperature', 'water_level', 'wind', 'air_temperature'
    begin_date : str
        开始日期 (YYYYMMDD)
    end_date : str
        结束日期 (YYYYMMDD)
    output_file : str
        输出CSV文件路径
    """
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": product,
        "application": "MGTA452_BlueTears_Project",
        "begin_date": begin_date,
        "end_date": end_date,
        "station": station,
        "time_zone": "gmt",
        "units": "metric",
        "format": "json"
    }

    print(f"📡 正在下载 {product} 数据...")
    print(f"   站点: {station}")
    print(f"   时间范围: {begin_date} - {end_date}")

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "data" not in data:
            print(f"❌ API返回无数据: {data}")
            return None

        # 转换为DataFrame
        df = pd.DataFrame(data["data"])

        # 重命名列
        if "t" in df.columns:
            df = df.rename(columns={"t": "datetime"})

        # 根据产品类型重命名数值列
        if product == "water_temperature" and "v" in df.columns:
            df = df.rename(columns={"v": "water_temp_c"})
        elif product == "wind" and "s" in df.columns:
            df = df.rename(columns={"s": "wind_speed_mps", "d": "wind_dir"})

        # 保存到CSV
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"✅ 成功保存到: {output_file}")
            print(f"   记录数: {len(df)}")
            print(f"   时间范围: {df['datetime'].min()} 到 {df['datetime'].max()}")

        return df

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 处理数据失败: {e}")
        return None


def download_ndbc_buoy(buoy_id="46254", year=2024, output_file=None):
    """
    从NDBC浮标下载标准气象数据

    Parameters:
    -----------
    buoy_id : str
        浮标ID (46254 = SCRIPPS Nearshore)
    year : int
        年份
    output_file : str
        输出CSV文件路径
    """
    # NDBC历史数据URL
    url = f"https://www.ndbc.noaa.gov/view_text_file.php?filename={buoy_id}h{year}.txt.gz&dir=data/historical/stdmet/"

    print(f"📡 正在下载NDBC浮标数据...")
    print(f"   浮标: {buoy_id}")
    print(f"   年份: {year}")

    try:
        # 读取固定宽度格式的文本文件
        df = pd.read_csv(url, sep=r'\s+', skiprows=[1])  # 跳过第二行（单位行）

        # 构建datetime列
        df['datetime'] = pd.to_datetime(
            df[['#YY', 'MM', 'DD', 'hh', 'mm']].rename(columns={
                '#YY': 'year', 'MM': 'month', 'DD': 'day',
                'hh': 'hour', 'mm': 'minute'
            })
        )

        # 选择关键列
        # WVHT = Wave Height, DPD = Dominant Wave Period, WTMP = Water Temp, WSPD = Wind Speed
        cols_to_keep = ['datetime']
        if 'WVHT' in df.columns:
            df['wave_height_m'] = pd.to_numeric(df['WVHT'], errors='coerce')
            cols_to_keep.append('wave_height_m')
        if 'WTMP' in df.columns:
            df['water_temp_c'] = pd.to_numeric(df['WTMP'], errors='coerce')
            cols_to_keep.append('water_temp_c')
        if 'WSPD' in df.columns:
            df['wind_speed_mps'] = pd.to_numeric(df['WSPD'], errors='coerce')
            cols_to_keep.append('wind_speed_mps')

        df = df[cols_to_keep].copy()

        # 替换NDBC的缺失值标记 (999.0, 99.0等)
        df = df.replace([99.0, 999.0, 9999.0], pd.NA)

        # 保存
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"✅ 成功保存到: {output_file}")
            print(f"   记录数: {len(df)}")
            print(f"   时间范围: {df['datetime'].min()} 到 {df['datetime'].max()}")
            print(f"   包含列: {[c for c in df.columns if c != 'datetime']}")

        return df

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None


def main():
    """主函数：下载所有数据"""
    print("=" * 70)
    print("La Jolla 蓝眼泪项目 - 真实数据下载")
    print("=" * 70)
    print()

    # 设置日期范围 (2024年全年)
    begin_date = "20240101"
    end_date = "20241231"
    year = 2024

    # 数据保存路径
    base_dir = "data"

    # 1. 下载NOAA水温数据
    print("\n" + "=" * 70)
    print("1. 下载水温数据 (NOAA)")
    print("=" * 70)
    water_temp_file = f"{base_dir}/water_temp_lajolla.csv"
    water_df = download_noaa_data(
        product="water_temperature",
        begin_date=begin_date,
        end_date=end_date,
        output_file=water_temp_file
    )
    time.sleep(2)  # 礼貌性延迟

    # 2. 下载NOAA风速数据
    print("\n" + "=" * 70)
    print("2. 下载风速数据 (NOAA)")
    print("=" * 70)
    wind_file = f"{base_dir}/wind_lajolla.csv"
    wind_df = download_noaa_data(
        product="wind",
        begin_date=begin_date,
        end_date=end_date,
        output_file=wind_file
    )
    time.sleep(2)

    # 3. 下载NDBC浮标数据 (浪高、水温、风速)
    print("\n" + "=" * 70)
    print("3. 下载浪高数据 (NDBC)")
    print("=" * 70)
    waves_file = f"{base_dir}/waves_lajolla.csv"
    ndbc_df = download_ndbc_buoy(
        buoy_id="46254",
        year=year,
        output_file=waves_file
    )

    # 总结
    print("\n" + "=" * 70)
    print("下载完成总结")
    print("=" * 70)

    success_count = 0
    if water_df is not None:
        print(f"✅ 水温数据: {water_temp_file}")
        success_count += 1
    else:
        print(f"❌ 水温数据下载失败")

    if wind_df is not None:
        print(f"✅ 风速数据: {wind_file}")
        success_count += 1
    else:
        print(f"❌ 风速数据下载失败")

    if ndbc_df is not None:
        print(f"✅ 浪高数据: {waves_file}")
        success_count += 1
    else:
        print(f"❌ 浪高数据下载失败")

    print(f"\n成功下载: {success_count}/3 个数据源")

    if success_count == 3:
        print("\n🎉 所有数据下载成功！")
        print("   现在可以运行notebook使用真实数据了")
    elif success_count > 0:
        print("\n⚠️  部分数据下载成功")
        print("   Notebook会对缺失的数据使用演示模式")
    else:
        print("\n❌ 所有数据下载失败")
        print("   请检查网络连接或稍后重试")
        print("   Notebook将使用演示数据运行")

    print("\n数据存储位置:")
    print(f"  - {base_dir}/water_temp_lajolla.csv")
    print(f"  - {base_dir}/wind_lajolla.csv")
    print(f"  - {base_dir}/waves_lajolla.csv")


if __name__ == "__main__":
    main()
