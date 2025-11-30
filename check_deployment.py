#!/usr/bin/env python3
"""
Pre-deployment checker for Blue Tears Dashboard
Verifies all required files exist before deployment
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "(required)" if required else "(optional)"
    print(f"{status} {filepath} {req_text}")
    return exists

def check_deployment_ready():
    """Check if all required files exist for deployment"""
    print("🔍 Checking deployment readiness...\n")
    
    all_good = True
    
    # Required files
    print("📄 Application Files:")
    all_good &= check_file_exists("app_en.py", required=True)
    all_good &= check_file_exists("requirements_streamlit.txt", required=True)
    
    print("\n📊 Data Files (in streamlit_data/):")
    data_files = [
        "streamlit_data/env_df_for_app.csv",
        "streamlit_data/scenario_results.csv",
        "streamlit_data/transactions_df.csv",
        "streamlit_data/feature_importance.csv",
    ]
    for df in data_files:
        all_good &= check_file_exists(df, required=True)
    
    # Optional but recommended
    check_file_exists("streamlit_data/classification_data.csv", required=False)
    
    print("\n⚙️ Configuration Files:")
    check_file_exists(".streamlit/config.toml", required=False)
    check_file_exists(".gitignore", required=False)
    
    print("\n" + "="*50)
    
    if all_good:
        print("✅ All required files present!")
        print("\n🚀 Ready to deploy!")
        print("\nNext steps:")
        print("1. Run: ./deploy.sh")
        print("2. Follow the instructions to push to GitHub")
        print("3. Deploy on https://share.streamlit.io")
        return 0
    else:
        print("❌ Some required files are missing!")
        print("\n📝 Please ensure all required files exist before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(check_deployment_ready())
