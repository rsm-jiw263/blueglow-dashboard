# La Jolla Blue Tears Dashboard - Deployment Guide

## 🌐 Live Demo
This Streamlit dashboard analyzes the commercial feasibility of La Jolla blue tears night tours.

## 🚀 Quick Deploy to Streamlit Cloud (FREE)

### Method 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Blue Tears Dashboard"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `app_en.py`
   - Click "Deploy"

3. **Done!** 
   Your app will be live at: `https://share.streamlit.io/YOUR_USERNAME/YOUR_REPO/app_en.py`

### Method 2: Heroku (Alternative)

Create `Procfile`:
```
web: sh setup.sh && streamlit run app_en.py
```

Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Method 3: Local Network Access

Share on your local network:
```bash
streamlit run app_en.py --server.address 0.0.0.0
```

Then share: `http://YOUR_LOCAL_IP:8501`

## 📦 Required Files

Make sure these files are in your repository:
- ✅ `app_en.py` (main application)
- ✅ `requirements_streamlit.txt` (dependencies)
- ✅ `streamlit_data/` folder (all CSV files)
- ✅ `.streamlit/config.toml` (configuration)

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements_streamlit.txt

# Run locally
streamlit run app_en.py
```

## 📊 Data Files Required

Ensure these CSV files exist in `streamlit_data/`:
- `env_df_for_app.csv`
- `scenario_results.csv`
- `transactions_df.csv`
- `feature_importance.csv`
- `classification_data.csv` (optional)

## 🎓 About

**Course**: MGTA 452 Business Analytics  
**Project**: La Jolla Blue Tears Commercial Feasibility Study  
**Tech Stack**: Python, Streamlit, Pandas, Scikit-learn, Matplotlib

## 📝 License

Educational project for MGTA 452 course.
