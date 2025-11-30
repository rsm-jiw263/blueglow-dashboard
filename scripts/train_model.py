#!/usr/bin/env python3
"""
Step 3: Train lightweight Logistic Regression model
使用弱监督银标规则 + 气候学特征训练模型
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLIM_FILE = os.path.join(ROOT, "data", "climatology.json")
MODEL_FILE = os.path.join(ROOT, "models", "biolum_lr.pkl")

def load_climatology():
    """加载气候学数据"""
    with open(CLIM_FILE, 'r') as f:
        return json.load(f)

def generate_weak_supervision_labels(n_samples=5000):
    """
    生成弱监督训练样本
    规则: 暗夜 + 低潮±2h + 低浪 → 高可能 (label=1)
          否则 → 低可能 (label=0)
    """
    print(f"🏷️  Generating {n_samples} weak supervision samples...")
    
    # 加载气候学数据
    clim = load_climatology()
    wave_doy = clim['wave_height_doy']
    temp_doy = clim['water_temp_doy']
    
    samples = []
    
    # 随机生成时间点 (过去一年)
    base_date = datetime(2024, 1, 1)
    
    for _ in range(n_samples):
        # 随机日期和时间
        random_days = np.random.randint(0, 365)
        random_hour = np.random.randint(0, 24)
        dt = base_date + timedelta(days=random_days, hours=random_hour)
        
        doy = dt.timetuple().tm_yday
        hour = dt.hour
        
        # 特征1: 月照度 (简化计算: 基于月相周期29.5天)
        days_since_new_moon = (random_days % 29.5)
        moon_illum = 1.0 - abs(days_since_new_moon - 14.75) / 14.75
        moon_illum = max(0.0, min(1.0, moon_illum))
        
        # 特征2: 是否夜间 (18:00-06:00)
        is_night = (hour >= 18 or hour <= 6)
        
        # 特征3: 潮汐相位 (简化: 基于M2周期12.42小时)
        hours_total = random_days * 24 + hour
        tide_phase = (hours_total / 12.42) * 2 * np.pi
        tide_level = np.cos(tide_phase)  # -1=低潮, 1=高潮
        
        # 特征4: 浪高气候值
        wave_height = float(wave_doy.get(str(doy), 1.0))
        
        # 特征5: 水温气候值
        water_temp = float(temp_doy.get(str(doy), 16.0))
        
        # 特征6: 季节 (归一化到0-1)
        season_norm = np.sin(2 * np.pi * doy / 365)
        
        # 弱监督规则
        dark_night = (moon_illum < 0.3) and is_night
        low_tide = (tide_level < -0.5)  # 低潮
        low_wave = (wave_height < 1.2)  # 浪高 < 1.2m
        
        # 银标: 满足3个条件 → 高可能
        label = 1 if (dark_night and low_tide and low_wave) else 0
        
        samples.append({
            'moon_illumination': moon_illum,
            'is_night': int(is_night),
            'tide_level': tide_level,
            'wave_height': wave_height,
            'water_temp': water_temp,
            'season_sin': season_norm,
            'label': label
        })
    
    df = pd.DataFrame(samples)
    
    print(f"   Positive samples (label=1): {df['label'].sum()} ({df['label'].mean()*100:.1f}%)")
    print(f"   Negative samples (label=0): {(1-df['label']).sum()}")
    
    return df

def train_model(df):
    """训练逻辑回归模型"""
    print("\n🤖 Training Logistic Regression model...")
    
    # 特征和标签
    feature_cols = ['moon_illumination', 'is_night', 'tide_level', 
                    'wave_height', 'water_temp', 'season_sin']
    
    X = df[feature_cols].values
    y = df['label'].values
    
    # 划分训练/测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    
    # 训练模型 (class_weight='balanced' 处理类别不平衡)
    model = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # 评估
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("\n📊 Model Performance:")
    print(classification_report(y_test, y_pred, target_names=['Low', 'High']))
    
    auc = roc_auc_score(y_test, y_prob)
    print(f"   ROC-AUC: {auc:.3f}")
    
    # 特征重要性
    print("\n📈 Feature Importance (Coefficients):")
    for feat, coef in zip(feature_cols, model.coef_[0]):
        print(f"   {feat:20s}: {coef:+.3f}")
    
    return model, feature_cols

def save_model(model, feature_cols):
    """保存模型"""
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    
    model_data = {
        'model': model,
        'feature_cols': feature_cols,
        'metadata': {
            'trained_at': datetime.utcnow().isoformat() + 'Z',
            'model_type': 'LogisticRegression',
            'features': feature_cols,
            'version': '1.0-climatology',
            'note': 'Trained with weak supervision. Ready for SST/Chl-a features when available.'
        }
    }
    
    joblib.dump(model_data, MODEL_FILE)
    print(f"\n✅ Model saved: {MODEL_FILE}")
    print(f"   Size: {os.path.getsize(MODEL_FILE)} bytes")

def main():
    print("=" * 60)
    print("�� BlueGlow - Step 3: Train Model")
    print("=" * 60)
    
    # 1. 生成弱监督样本
    df = generate_weak_supervision_labels(n_samples=5000)
    
    # 2. 训练模型
    model, feature_cols = train_model(df)
    
    # 3. 保存模型
    save_model(model, feature_cols)
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("   Next: Run step4_forecast.sh to generate predictions")
    print("=" * 60)

if __name__ == "__main__":
    main()
