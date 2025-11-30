#!/usr/bin/env python3
"""
Fetch historical data with mirrors, fallback datasets, and retry backoff
智能容错：主源失败→切镜像→换备选数据集→指数退避重试
"""

import os, sys, io, math, time, json, glob, gzip
from datetime import datetime, timedelta
import requests
import pandas as pd
from erddapy import ERDDAP
from dotenv import dotenv_values
import ssl

# Fix SSL certificate issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = {**dotenv_values(os.path.join(ROOT,"config",".env"))}

def cfg_float(key, default):
    try: return float(CFG.get(key, default))
    except: return default

def cfg_int(key, default):
    try: return int(CFG.get(key, default))
    except: return default

LAT_MIN=cfg_float("LAT_MIN",32.83); LAT_MAX=cfg_float("LAT_MAX",32.89)
LON_MIN=cfg_float("LON_MIN",-117.32); LON_MAX=cfg_float("LON_MAX",-117.20)

def parse_date(s):
    if not s: return None
    return datetime.fromisoformat(s.replace("Z",""))

START = parse_date(CFG.get("START","")) or (datetime.utcnow() - timedelta(days=365*2))
END   = parse_date(CFG.get("END",""))   or datetime.utcnow()
if START > END: START, END = END, START

NDBC_STATION = CFG.get("NDBC_STATION","46254")

# Primary sources
SST_PRIMARY = (
    CFG.get("ERDDAP_CW","https://coastwatch.pfeg.noaa.gov/erddap"), 
    CFG.get("SST_DATASET","jplMURSST41"), 
    CFG.get("SST_VAR","sst")
)
SST_FALLBACKS = [tuple(x.split("|")) for x in (CFG.get("SST_FALLBACKS","").split(",") if CFG.get("SST_FALLBACKS") else [])]

CHLA_PRIMARY = (
    CFG.get("CHLA_SERVER","https://coastwatch.noaa.gov/erddap"), 
    CFG.get("CHLA_DATASET","noaacwNPPVIIRSchlaDaily"), 
    CFG.get("CHLA_VAR","chlor_a")
)
CHLA_FALLBACKS = [tuple(x.split("|")) for x in (CFG.get("CHLA_FALLBACKS","").split(",") if CFG.get("CHLA_FALLBACKS") else [])]

CHUNK_MONTHS = cfg_int("CHUNK_MONTHS",1)
TIMEOUT = cfg_int("TIMEOUT",120)
RETRY_TIMES = cfg_int("RETRY_TIMES",3)
RETRY_BACKOFF = cfg_int("RETRY_BACKOFF_SEC",15)

RAW_DIR = os.path.join(ROOT,"data","raw")
os.makedirs(RAW_DIR, exist_ok=True)

def month_range(start, end, step=1):
    cur = datetime(start.year, start.month, 1)
    endm = datetime(end.year, end.month, 1)
    while cur <= endm:
        yield cur
        m = cur.month - 1 + step
        y = cur.year + m // 12
        m = m % 12 + 1
        cur = datetime(y, m, 1)

def month_end(d):
    if d.month==12: return datetime(d.year,12,31,23,59,59)
    return datetime(d.year, d.month+1, 1) - timedelta(seconds=1)

def get_grid(server, dataset_id, var, t0, t1):
    e = ERDDAP(server=server, protocol="griddap")
    e.dataset_id = dataset_id
    e.variables = [var]
    e.constraints = {
        "time>=": t0.strftime("%Y-%m-%dT00:00:00Z"),
        "time<=": t1.strftime("%Y-%m-%dT23:59:59Z"),
        "latitude>=": LAT_MIN, "latitude<=": LAT_MAX,
        "longitude>=": LON_MIN, "longitude<=": LON_MAX
    }
    url = e.get_download_url(response="netcdf")
    
    last_err = None
    for attempt in range(1, RETRY_TIMES+1):
        try:
            r = requests.get(url, timeout=TIMEOUT, verify=False)
            if r.status_code == 200 and r.content and len(r.content) > 200:
                return r.content
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
        
        if attempt < RETRY_TIMES:
            wait_time = RETRY_BACKOFF * attempt
            print(f"    Retry {attempt}/{RETRY_TIMES-1} after {wait_time}s...")
            time.sleep(wait_time)
    
    raise RuntimeError(last_err or "unknown error")

def fetch_with_fallback(out_path, prim, fallbacks, t0, t1, tag):
    if os.path.exists(out_path):
        print(f"✓ Skip {out_path}")
        return True
    
    servers = [prim] + fallbacks
    for i, (server, dataset, var) in enumerate(servers):
        source_label = "Primary" if i == 0 else f"Fallback {i}"
        try:
            print(f"\n[{tag}] {t0.date()}→{t1.date()} | {source_label} ({i+1}/{len(servers)})")
            print(f"  Server: {server}")
            print(f"  Dataset: {dataset}")
            print(f"  Variable: {var}")
            
            content = get_grid(server, dataset, var, t0, t1)
            
            with open(out_path, "wb") as f:
                f.write(content)
            
            size_mb = len(content) / 1024 / 1024
            print(f"  ✅ Saved: {os.path.basename(out_path)} ({size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            continue
    
    print(f"  ⚠️  All {len(servers)} source(s) failed for {t0.date()}→{t1.date()}")
    return False

def fetch_series(primary, fallbacks, prefix, tag):
    print(f"\n{'='*60}")
    print(f"📊 {tag} Time Series")
    print(f"{'='*60}")
    
    success_count = 0
    fail_count = 0
    
    for m in month_range(START, END, CHUNK_MONTHS):
        t0 = m
        t1 = min(month_end(m), END)
        if t1 < START:
            continue
        
        out = os.path.join(RAW_DIR, f"{prefix}_{m.strftime('%Y%m')}.nc")
        
        if fetch_with_fallback(out, primary, fallbacks, t0, t1, tag):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ {tag}: {success_count} files downloaded successfully")
    if fail_count > 0:
        print(f"⚠️  {tag}: {fail_count} files failed")
    print(f"{'='*60}")

def fetch_ndbc_hist():
    print(f"\n{'='*60}")
    print("💨 NDBC Wind Data (Historical stdmet)")
    print(f"{'='*60}")
    
    y0, y1 = START.year, END.year
    out_csv = os.path.join(RAW_DIR, f"ndbc_{NDBC_STATION}_{y0}_{y1}.csv")
    
    if os.path.exists(out_csv):
        print(f"✓ Skip {out_csv}")
        return
    
    frames = []
    for y in range(y0, y1+1):
        url = f"https://www.ndbc.noaa.gov/data/historical/stdmet/{NDBC_STATION}h{y}.txt.gz"
        ok = False
        
        for attempt in range(1, RETRY_TIMES+1):
            try:
                print(f"\n📥 Fetching year {y} (attempt {attempt}/{RETRY_TIMES})")
                print(f"  URL: {url}")
                
                r = requests.get(url, timeout=TIMEOUT)
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}")
                
                with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as g:
                    text = g.read().decode("utf-8", errors="ignore")
                
                lines = [ln for ln in text.splitlines() if not ln.startswith("#")]
                parts = [ln.split() for ln in lines if ln.strip()]
                
                if not parts:
                    raise RuntimeError("empty file")
                
                header_row = parts[0]
                data_rows = parts[1:]
                
                if not data_rows:
                    continue
                
                ncols = len(data_rows[0])
                std_cols = ["YY","MM","DD","hh","mm","WDIR","WSPD","GST","WVHT","DPD","APD","MWD","PRES","ATMP","WTMP","DEWP","VIS","PTDY","TIDE"]
                cols = std_cols[:ncols]
                
                df = pd.DataFrame(data_rows, columns=cols)
                
                for c in ["YY","MM","DD","hh","mm"]:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors="coerce")
                
                if "WSPD" in df.columns:
                    df["WSPD"] = pd.to_numeric(df["WSPD"], errors="coerce")
                
                try:
                    df["dt"] = pd.to_datetime(
                        df[["YY","MM","DD","hh","mm"]].rename(
                            columns={"YY":"year","MM":"month","DD":"day","hh":"hour","mm":"minute"}
                        ),
                        errors="coerce", utc=True
                    )
                except Exception:
                    pass
                
                frames.append(df)
                ok = True
                print(f"  ✅ Year {y}: {len(df):,} rows")
                break
                
            except Exception as e:
                print(f"  ❌ Warning: {e}")
                if attempt < RETRY_TIMES:
                    wait_time = RETRY_BACKOFF * attempt
                    print(f"    Retrying after {wait_time}s...")
                    time.sleep(wait_time)
        
        if not ok:
            print(f"  ⚠️  Skipped year {y}")
    
    if frames:
        allf = pd.concat(frames, ignore_index=True)
        allf.to_csv(out_csv, index=False)
        print(f"\n✅ Saved: {os.path.basename(out_csv)}")
        print(f"   Total rows: {len(allf):,}")
        print(f"   Years: {y0}-{y1}")
    else:
        print("\n⚠️  No NDBC files downloaded")

def main():
    print("\n" + "="*60)
    print("🌊 BlueGlow - Step 2: Fetch Historical Data")
    print("   (with mirrors, fallbacks & retry backoff)")
    print("="*60)
    print(f"📅 Time range: {START.date()} → {END.date()}")
    print(f"📍 Bbox: ({LAT_MIN}, {LON_MIN}) → ({LAT_MAX}, {LON_MAX})")
    print(f"�� NDBC Station: {NDBC_STATION}")
    print(f"🔄 Retry: {RETRY_TIMES} times with {RETRY_BACKOFF}s backoff")
    print(f"📂 Output: {RAW_DIR}")
    print("="*60)
    
    os.makedirs(RAW_DIR, exist_ok=True)
    
    print(f"\n💡 SST sources: {len([SST_PRIMARY] + SST_FALLBACKS)} configured")
    fetch_series(SST_PRIMARY, SST_FALLBACKS, "sst", "SST")
    
    print(f"\n💡 Chl-a sources: {len([CHLA_PRIMARY] + CHLA_FALLBACKS)} configured")
    fetch_series(CHLA_PRIMARY, CHLA_FALLBACKS, "chla", "CHLA")
    
    fetch_ndbc_hist()
    
    print("\n" + "="*60)
    print("✅ All downloads complete!")
    print(f"📂 Files saved in: {RAW_DIR}")
    print("="*60)
    print("\n💡 Next: Run validation script to check data quality")
    print("   bash validate_step2.sh")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
