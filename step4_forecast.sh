#!/bin/bash
# Step 4: Generate 7-day forecast using trained model
set -e

echo "============================================================"
echo "BlueGlow - Step 4: Generate 7-Day Forecast"
echo "============================================================"

source .venv/bin/activate

# Ensure model exists
if [ ! -f "models/biolum_lr.pkl" ]; then
    echo "WARNING: Model not found. Running training first..."
    bash step3_train.sh
fi

# Ensure astronomy data exists
if [ ! -f "data/astronomy_next7.json" ]; then
    echo "Computing astronomy data..."
    python scripts/compute_astronomy.py
fi

# Generate forecast
python scripts/forecast_next7.py

echo ""
echo "[DONE] Forecast complete!"
echo "   Next: Open http://localhost:5500 to view"
