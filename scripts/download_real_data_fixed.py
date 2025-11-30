#!/usr/bin/env python3
"""
下载La Jolla真实环境数据（修复版）
- 解决NOAA 31天限制（分批下载）
- 解决NDBC SSL证书问题（禁用验证）
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import urllib3
import ssl

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_noaa_chunked(product, output_file, station='9410230', 
                          begin_date='20240101', end_date='20241231'):
    """
    从NOAA API下载数据（分批下载避免31天限制）
    
    参数:
        product: 'water_temperature', 'wind', 'air_temperature', 'water_level'
        output_file: CSV文件保存路径
        station: 站点ID (默认9410230 = La Jolla/Scripps Pier)
        begin_date/end_date: YYYYMMDD格式
    """
    base_url = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
    
    start_dt = datetime.strptime(begin_date, '%Y%m%d')
    end_dt = datetime.strptime(end_date, '%Y%m%d')
    
    all_data = []
    current_dt = start_dt
    chunk_days = 30  # 每次请求30天
    
    print(f"\n📡 下载 NOAA {product} 数据")
    print(f"   站点: {station}")
    print(f"   范围: {begin_date} → {end_date}")
    print(f"   策略: 每次30天分批请求")
    
    batch_num = 0
    while current_dt <= end_dt:
        batch_num += 1
        chunk_end = min(current_dt + timedelta(days=chunk_days), end_dt)
        
        chunk_begin = current_dt.strftime('%Y%m%d')
        chunk_end_str = chunk_end.strftime('%Y%m%d')
        
        params = {
            'begin_date': chunk_begin,
            'end_date': chunk_end_str,
            'station': station,
            'product': product,
            'datum': 'MLLW',
            'time_zone': 'GMT',
            'units': 'metric',
            'format': 'json',
            'application': 'MGTA452_BlueGlow_Project'
        }
        
        print(f"   批次{batch_num}: {chunk_begin} → {chunk_end_str} ... ", end="", flush=True)
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                print(f"⚠️ {data['error'].get('message', 'API错误')}")
                current_dt = chunk_end + timedelta(days=1)
                continue
            
            if 'data' in data and len(data['data']) > 0:
                all_data.extend(data['data'])
                print(f"✓ {len(data['data'])}条")
            else:
                print("⚠️ 无数据")
            
            time.sleep(0.5)  # 避免请求过快
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP {response.status_code}")
            if response.status_code == 400:
                print(f"      可能原因: 该站点不提供 {product} 数据")
        except Exception as e:
            print(f"❌ {type(e).__name__}: {str(e)[:50]}")
        
        current_dt = chunk_end + timedelta(days=1)
    
    # 保存数据
    if len(all_data) > 0:
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False)
        print(f"   ✅ 总共 {len(df)} 条记录 → {output_file}\n")
        return True
    else:
        print(f"   ❌ 未获取任何数据\n")
        return False


def download_ndbc_buoy(buoy_id='46254', year='2024', output_file=None):
    """
    从NDBC下载浮标数据（禁用SSL验证）
    
    参数:
        buoy_id: 浮标ID (46254 = SCRIPPS Nearshore)
        year: 年份
        output_file: CSV保存路径
    """
    # NDBC标准气象数据文件格式
    url = f'https://www.ndbc.noaa.gov/view_text_file.php?filename={buoy_id}h{year}.txt.gz&dir=data/historical/stdmet/'
    
    print(f"\n🌊 下载 NDBC 浮标 {buoy_id} 数据")
    print(f"   年份: {year}")
    print(f"   URL: {url}")
    
    try:
        # 禁用SSL证书验证
        response = requests.get(url, timeout=60, verify=False)
        response.raise_for_status()
        
        # NDBC文件是文本格式，需要解析
        lines = response.text.strip().split('\n')
        
        if len(lines) < 3:
            print(f"   ❌ 文件格式不正确\n")
            return False
        
        # 第一行是列名，第二行是单位，第三行开始是数据
        header = lines[0].split()
        units = lines[1].split()
        data_lines = lines[2:]
        
        # 解析数据
        data_rows = []
        for line in data_lines:
            parts = line.split()
            if len(parts) >= len(header):
                data_rows.append(parts[:len(header)])
        
        if len(data_rows) == 0:
            print(f"   ❌ 无有效数据行\n")
            return False
        
        df = pd.DataFrame(data_rows, columns=header)
        
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"   ✅ {len(df)} 条记录 → {output_file}\n")
        
        return True
        
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL证书错误（已尝试禁用验证）: {str(e)[:80]}\n")
        return False
    except Exception as e:
        print(f"   ❌ {type(e).__name__}: {str(e)[:80]}\n")
        return False


def main():
    """主下载流程"""
    print("=" * 60)
    print("🌊 La Jolla 蓝眼泪项目 - 真实环境数据下载")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    # 1. NOAA水温数据
    total_count += 1
    if download_noaa_chunked(
        product='water_temperature',
        output_file='data/water_temp_lajolla.csv',
        station='9410230',
        begin_date='20240101',
        end_date='20241231'
    ):
        success_count += 1
    
    # 2. NOAA风速数据
    total_count += 1
    if download_noaa_chunked(
        product='wind',
        output_file='data/wind_lajolla.csv',
        station='9410230',
        begin_date='20240101',
        end_date='20241231'
    ):
        success_count += 1
    
    # 3. NOAA气温数据（额外尝试）
    total_count += 1
    if download_noaa_chunked(
        product='air_temperature',
        output_file='data/air_temp_lajolla.csv',
        station='9410230',
        begin_date='20240101',
        end_date='20241231'
    ):
        success_count += 1
    
    # 4. NDBC浮标浪高数据
    total_count += 1
    if download_ndbc_buoy(
        buoy_id='46254',
        year='2024',
        output_file='data/waves_lajolla.csv'
    ):
        success_count += 1
    
    # 总结
    print("=" * 60)
    print(f"📊 下载完成: {success_count}/{total_count} 个数据源成功")
    print("=" * 60)
    
    if success_count > 0:
        print("\n✅ 已下载的文件:")
        import os
        for fname in ['water_temp_lajolla.csv', 'wind_lajolla.csv', 
                      'air_temp_lajolla.csv', 'waves_lajolla.csv']:
            fpath = f'data/{fname}'
            if os.path.exists(fpath):
                size = os.path.getsize(fpath)
                print(f"   • {fpath} ({size:,} bytes)")
    
    if success_count == 0:
        print("\n⚠️  所有数据源均下载失败")
        print("\n🔧 替代方案:")
        print("   1. 手动下载NOAA数据:")
        print("      https://tidesandcurrents.noaa.gov/waterlevels.html?id=9410230")
        print("   2. 手动下载NDBC数据:")
        print("      https://www.ndbc.noaa.gov/station_page.php?station=46254")
        print("   3. 使用笔记本中的demo数据（自动fallback）")
        print("\n详细说明见: data/README_DATA_ACQUISITION.md")
    
    return success_count


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success > 0 else 1)
