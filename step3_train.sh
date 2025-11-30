#!/bin/bash
# Step 3: Train Logistic Regression model with weak supervision
set -e

echo "============================================================"
echo "BlueGlow - Step 3: Train Model"
echo "============================================================"

source .venv/bin/activate

# Ensure climatology data exists
if [ ! -f "data/climatology.json" ]; then
    echo "Computing climatology first..."
    python scripts/compute_climatology.py
fi

# Train the model
python scripts/train_model.py

echo ""
echo "[DONE] Model training complete!"
echo "   Next: Run step4_forecast.sh"
