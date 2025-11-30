#!/usr/bin/env python3
"""
Step 2 数据验收脚本
快速检查下载的 NetCDF 和 CSV 文件质量
"""

import glob
import os

def check_netcdf():
    """检查 NetCDF (SST/Chl-a) 文件"""
    print("=" * 60)
    print("📊 检查 NetCDF 文件 (SST & Chl-a)")
    print("=" * 60)
    
    try:
        import xarray as xr
        
        # Check SST files
        sst_files = sorted(glob.glob('data/raw/sst_*.nc'))
        print(f"\n✅ SST 文件数量: {len(sst_files)}")
        
        if sst_files:
            print(f"\n📁 SST 文件列表:")
            for f in sst_files:
                size_mb = os.path.getsize(f) / 1024 / 1024
                print(f"  - {os.path.basename(f)}: {size_mb:.2f} MB")
            
            print(f"\n🔍 SST 样本检查 ({os.path.basename(sst_files[0])}):")
            ds = xr.open_dataset(sst_files[0])
            print(f"  维度: {dict(ds.dims)}")
            print(f"  时间范围: {str(ds.time.values.min())[:19]} → {str(ds.time.values.max())[:19]}")
            print(f"  纬度范围: {float(ds.latitude.values.min()):.4f} → {float(ds.latitude.values.max()):.4f}")
            print(f"  经度范围: {float(ds.longitude.values.min()):.4f} → {float(ds.longitude.values.max()):.4f}")
            print(f"  变量: {list(ds.data_vars.keys())}")
            
            # Check for missing values
            if 'sst' in ds:
                sst_data = ds.sst.values
                import numpy as np
                valid_pct = (1 - np.isnan(sst_data).sum() / sst_data.size) * 100
                print(f"  数据完整度: {valid_pct:.1f}%")
            
            ds.close()
        else:
            print("⚠️  未找到 SST 文件")
        
        # Check Chl-a files
        chla_files = sorted(glob.glob('data/raw/chla_*.nc'))
        print(f"\n✅ Chl-a 文件数量: {len(chla_files)}")
        
        if chla_files:
            print(f"\n📁 Chl-a 文件列表:")
            for f in chla_files:
                size_mb = os.path.getsize(f) / 1024 / 1024
                print(f"  - {os.path.basename(f)}: {size_mb:.2f} MB")
            
            print(f"\n🔍 Chl-a 样本检查 ({os.path.basename(chla_files[0])}):")
            dc = xr.open_dataset(chla_files[0])
            print(f"  维度: {dict(dc.dims)}")
            print(f"  时间范围: {str(dc.time.values.min())[:19]} → {str(dc.time.values.max())[:19]}")
            print(f"  纬度范围: {float(dc.latitude.values.min()):.4f} → {float(dc.latitude.values.max()):.4f}")
            print(f"  经度范围: {float(dc.longitude.values.min()):.4f} → {float(dc.longitude.values.max()):.4f}")
            print(f"  变量: {list(dc.data_vars.keys())}")
            dc.close()
        else:
            print("⚠️  未找到 Chl-a 文件")
            
    except ImportError:
        print("❌ xarray 未安装,无法检查 NetCDF 文件")
    except Exception as e:
        print(f"❌ NetCDF 检查出错: {e}")

def check_ndbc():
    """检查 NDBC CSV 文件"""
    print("\n" + "=" * 60)
    print("💨 检查 NDBC 风速数据")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        ndbc_files = sorted(glob.glob('data/raw/ndbc_46254_*.csv'))
        
        if not ndbc_files:
            print("⚠️  未找到 NDBC 文件")
            return
        
        print(f"\n✅ NDBC 文件数量: {len(ndbc_files)}")
        
        for f in ndbc_files:
            size_mb = os.path.getsize(f) / 1024 / 1024
            print(f"\n📁 文件: {os.path.basename(f)} ({size_mb:.2f} MB)")
            
            df = pd.read_csv(f)
            print(f"  总行数: {len(df):,}")
            print(f"  列数: {len(df.columns)}")
            print(f"  列名: {list(df.columns[:10])}...")
            
            if 'dt' in df.columns:
                df['dt'] = pd.to_datetime(df['dt'])
                print(f"  时间范围: {df['dt'].min()} → {df['dt'].max()}")
            
            if 'WSPD' in df.columns:
                df['WSPD'] = pd.to_numeric(df['WSPD'], errors='coerce')
                valid_wspd = df['WSPD'][df['WSPD'] < 90].dropna()
                if len(valid_wspd) > 0:
                    print(f"  风速统计 (m/s):")
                    print(f"    - 平均: {valid_wspd.mean():.2f}")
                    print(f"    - 范围: {valid_wspd.min():.2f} → {valid_wspd.max():.2f}")
                    print(f"    - 有效数据点: {len(valid_wspd):,} ({len(valid_wspd)/len(df)*100:.1f}%)")
            
            print(f"\n  样本数据 (前5行):")
            print(df[['dt', 'WSPD', 'WDIR']].head().to_string(index=False) if 'dt' in df.columns and 'WSPD' in df.columns else df.head())
            
    except ImportError:
        print("❌ pandas 未安装,无法检查 CSV 文件")
    except Exception as e:
        print(f"❌ NDBC 检查出错: {e}")

def check_summary():
    """总体摘要"""
    print("\n" + "=" * 60)
    print("📊 数据下载总结")
    print("=" * 60)
    
    sst_count = len(glob.glob('data/raw/sst_*.nc'))
    chla_count = len(glob.glob('data/raw/chla_*.nc'))
    ndbc_count = len(glob.glob('data/raw/ndbc_*.csv'))
    
    # Calculate total size
    all_files = glob.glob('data/raw/*')
    total_size = sum(os.path.getsize(f) for f in all_files if os.path.isfile(f))
    total_size_mb = total_size / 1024 / 1024
    
    print(f"\n文件统计:")
    print(f"  ✅ SST (NetCDF): {sst_count} 个文件")
    print(f"  ✅ Chl-a (NetCDF): {chla_count} 个文件")
    print(f"  ✅ NDBC (CSV): {ndbc_count} 个文件")
    print(f"  📦 总大小: {total_size_mb:.2f} MB")
    
    # Expected files (23 months from 2024-01 to 2025-11)
    expected_months = 23
    print(f"\n预期月份数: {expected_months}")
    
    if sst_count == expected_months and chla_count == expected_months:
        print("✅ 数据完整!")
    else:
        print(f"⚠️  可能缺少部分月份数据")
        if sst_count < expected_months:
            print(f"   - SST 缺少 {expected_months - sst_count} 个月")
        if chla_count < expected_months:
            print(f"   - Chl-a 缺少 {expected_months - chla_count} 个月")
    
    print("\n" + "=" * 60)
    print("验收完成! 可以继续 Step 3 训练模型")
    print("=" * 60)

def main():
    print("\n🌊 BlueGlow Step 2 - 数据验收\n")
    
    if not os.path.exists('data/raw'):
        print("❌ data/raw 目录不存在,请先运行 step2_fetch_data.sh")
        return
    
    check_netcdf()
    check_ndbc()
    check_summary()

if __name__ == "__main__":
    main()
