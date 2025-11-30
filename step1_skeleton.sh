#!/bin/bash
# Step 1: Create skeleton structure with demo forecast

echo "Creating skeleton structure..."

# Activate virtual environment
source .venv/bin/activate

# Create necessary directories
mkdir -p data
mkdir -p models
mkdir -p scripts
mkdir -p site/assets/css
mkdir -p site/assets/js

# Run Python script to generate demo data
python scripts/generate_demo_forecast.py

echo "[DONE] Skeleton structure created with demo forecast data"
