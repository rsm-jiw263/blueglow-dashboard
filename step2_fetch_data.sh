#!/bin/bash
# Step 2: Fetch real historical data

echo "Step 2: Fetching historical data..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Create config/.env if it doesn't exist
if [ ! -f "config/.env" ]; then
    echo "Creating config/.env from example..."
    cp config/.env.example config/.env
    echo "[DONE] config/.env created. You can edit it to customize the settings."
    echo ""
fi

# Run data fetching script
echo "Starting data download..."
python scripts/fetch_static.py

echo ""
echo "[DONE] Step 2 complete!"
echo "Raw data files saved in: data/raw/"
echo "Next: Run 'Step3: Train' to process the data and train the model"
