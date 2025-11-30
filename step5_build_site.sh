#!/bin/bash
# Step 5: Build website

echo "Building website..."

# Activate virtual environment
source .venv/bin/activate

# Run site builder script
python scripts/build_site.py

echo "[DONE] Website built successfully!"
echo "Run 'Site: Preview' task to view at http://localhost:5500"
