#!/bin/bash

# Blue Tears Dashboard - Quick Deploy Script

echo "🚀 Blue Tears Dashboard Deployment Helper"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.vscode/
.DS_Store
*.csv.bak
*.log
EOF
    echo "✅ .gitignore created"
fi

echo ""
echo "📋 Next Steps to Deploy:"
echo ""
echo "1️⃣  Create a GitHub repository at https://github.com/new"
echo ""
echo "2️⃣  Run these commands:"
echo "    git add ."
echo "    git commit -m 'Initial commit - Blue Tears Dashboard'"
echo "    git remote add origin YOUR_GITHUB_REPO_URL"
echo "    git push -u origin main"
echo ""
echo "3️⃣  Deploy to Streamlit Cloud:"
echo "    • Go to https://share.streamlit.io"
echo "    • Sign in with GitHub"
echo "    • Click 'New app'"
echo "    • Select your repository"
echo "    • Main file: app_en.py"
echo "    • Advanced settings:"
echo "      - Python version: 3.9+"
echo "      - Requirements file: requirements_streamlit.txt"
echo "    • Click 'Deploy'"
echo ""
echo "4️⃣  Your app will be live at:"
echo "    https://YOUR_USERNAME-YOUR_REPO.streamlit.app"
echo ""
echo "🎉 That's it! Your dashboard will be accessible worldwide!"
echo ""
echo "📚 Need help? Check README_DEPLOYMENT.md"
