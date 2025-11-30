#!/bin/bash
# Setup virtual environment and install dependencies

echo "Setting up virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "[DONE] Virtual environment created"
else
    echo "[DONE] Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "[DONE] Setup complete!"
echo "Next steps:"
echo "   1. Run 'Step1: Skeleton (demo forecast)' to create initial structure"
echo "   2. Optionally run Steps 2-4 for data fetching and training"
echo "   3. Run 'Step5: Build site' to generate the website"
echo "   4. Run 'Site: Preview' to view the site"
