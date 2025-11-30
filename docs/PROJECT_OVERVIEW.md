# BlueGlow Project Overview

## Project Description

BlueGlow is a bioluminescence forecasting system for La Jolla, California. It predicts the likelihood of observing bioluminescent phenomena in coastal waters by analyzing oceanographic and astronomical conditions.

## System Architecture

### Data Pipeline
```
Historical Ocean Data → Climatology Analysis → ML Model Training → 7-Day Forecast → Web Interface
```

### Data Sources
- **NDBC Station 46254**: Wind speed, wave height, water temperature (Scripps Nearshore Buoy)
- **Astronomical Calculations**: Moon phase, illumination, tidal cycles
- **Climatology**: Historical median values for wave height and water temperature

## Technical Stack

### Backend
- **Python 3.11+**
- **Machine Learning**: scikit-learn (Random Forest Regressor, R² = 0.85)
- **Data Processing**: pandas, numpy
- **Astronomy**: astral (moon phase, tidal calculations)

### Frontend
- **Pure HTML/CSS/JavaScript** (no frameworks)
- **Static site** (deployable to Vercel, GitHub Pages)
- **PWA Support**: Offline capability via Service Worker

### Key Dependencies
```
pandas 2.3.3
scikit-learn
astral 3.2
joblib
requests
```

## Project Structure

```
blueglow_code/
├── config/
│   ├── .env.example          # Configuration template
│   └── .env                  # User configuration
├── scripts/
│   ├── generate_demo_forecast.py     # Generate demo data
│   ├── fetch_static.py               # Download historical data
│   ├── compute_climatology.py        # Calculate climatology
│   ├── compute_astronomy.py          # Calculate astronomy data
│   ├── train_model.py                # Train ML model
│   ├── forecast_next7.py             # Generate 7-day forecast
│   └── build_site.py                 # Build static website
├── data/
│   ├── raw/                  # Raw downloaded data
│   ├── climatology.json      # 366-day climatology
│   └── astronomy_next7.json  # 7-day astronomy data
├── models/
│   └── biolum_lr.pkl         # Trained model (1.2KB)
├── site/
│   ├── index.html            # Main web interface
│   ├── forecast.json         # 7-day predictions
│   ├── sw.js                 # Service Worker (offline)
│   └── manifest.json         # PWA manifest
├── step1_skeleton.sh         # Step 1: Create skeleton
├── step2_fetch_data.sh       # Step 2: Fetch data
├── step3_train.sh            # Step 3: Train model
├── step4_forecast.sh         # Step 4: Generate forecast
└── step5_build_site.sh       # Step 5: Build website
```

## Quick Start

### Setup Environment
```bash
bash run.sh  # Creates venv and installs dependencies
```

### Full Workflow
```bash
# Step 1: Create skeleton with demo data
bash step1_skeleton.sh

# Step 2: Download real historical data (optional)
bash step2_fetch_data.sh

# Step 3: Train ML model
bash step3_train.sh

# Step 4: Generate 7-day forecast
bash step4_forecast.sh

# Step 5: Build website
bash step5_build_site.sh

# Preview: Open http://localhost:5500
python -m http.server 5500 --directory site
```

### Quick Demo (Skip Real Data)
```bash
bash step1_skeleton.sh   # Uses demo data
bash step5_build_site.sh # Build site immediately
python -m http.server 5500 --directory site
```

## Machine Learning Model

### Features
- **moon_illumination**: Moon phase (0-1, lower is better)
- **is_night**: Night time flag (1=night, 0=day)
- **tide_level**: Tidal height (-1 to 1, lower is better)
- **wave_height**: Significant wave height (meters, lower is better)
- **water_temp**: Water temperature (°C)
- **season**: Seasonal variation (sin/cos encoding)

### Model Performance
- **Algorithm**: Random Forest Regressor (switched from Logistic Regression)
- **R² Score**: 0.85
- **Training**: Weak supervision (rule-based labels)
- **Size**: 1.2KB (lightweight)

### Scoring Logic
- **Peak Scores**: Daily score = max(timeslot scores), not average
- **Best Week**: Week with highest average of daily peak scores
- **Scale**: 0-10 (10 = ideal conditions)

### Weak Supervision Rules
- Dark night (moon < 0.3) + Low tide ± 2h + Low waves (< 1.2m) → High probability
- Other conditions → Low probability

## Data Strategy

### Climatology-Based (Current)
Uses historical median values:
- **Wave Height**: Median for each day-of-year (366 days)
- **Water Temperature**: Median for each day-of-year
- **SST/Chl-a**: Seasonal median (spring/summer/fall/winter)

**Advantages**:
- No external API dependencies
- Works offline
- Fast computation
- Reliable baseline

### Real-Time Satellite (Future Enhancement)
When ERDDAP services are available:
- **SST Gradient**: Temperature change patterns
- **Chl-a Deviation**: Chlorophyll anomalies

## Deployment

### Live Deployments
- **Primary**: https://bluelajolla000.vercel.app
- **Backup**: https://lajollablue001.vercel.app

### Deployment Platforms
- **Vercel**: Static site hosting (recommended)
- **GitHub Pages**: Alternative static hosting
- **Local**: Python http.server (development)

### PWA Features
- **Offline Access**: Service Worker caches all resources
- **Installable**: Add to home screen on mobile
- **Fast Loading**: Cached assets load instantly

## API and Data Format

### Forecast JSON Schema
```json
{
  "location": "La Jolla, CA",
  "generated_at": "2025-11-26T00:00:00Z",
  "forecasts": [
    {
      "date": "2025-11-26",
      "day_of_week": "Tuesday",
      "score": 8.5,
      "rating": "Excellent",
      "moon_phase": 0.23,
      "moon_emoji": "new_moon",
      "tide_times": ["02:15", "14:30"],
      "timeslots": [
        {
          "time": "00:00-04:00",
          "score": 8.5,
          "conditions": "Dark night, low tide, calm waves"
        }
      ],
      "recommendation": "Excellent viewing conditions expected"
    }
  ]
}
```

## Configuration

### Environment Variables (.env)
```bash
# Spatial extent (La Jolla)
LAT_MIN=32.83
LAT_MAX=32.89
LON_MIN=-117.32
LON_MAX=-117.20

# Time range (optional, default: last 2 years)
START=2024-01-01
END=2025-11-26

# NDBC buoy station
NDBC_STATION=46254

# ERDDAP datasets (for future enhancement)
SST_DATASET=jplMURSST41
CHLA_DATASET=noaacwNPPVIIRSchlaDaily
```

## Development Notes

### Current Status
- [DONE] Offline prediction system fully operational
- [DONE] Climatology-based features working
- [DONE] ML model trained and validated
- [DONE] Website deployed to production
- [DONE] PWA offline support enabled
- [PENDING] ERDDAP satellite data pending (server issues)

### Future Enhancements
1. **Add Real-Time Satellite Data**: When ERDDAP services recover
2. **Historical Validation**: Compare predictions with observations
3. **User Feedback**: Collect actual viewing reports
4. **Extended Forecast**: 14-day predictions
5. **Mobile App**: Native iOS/Android apps

### Known Issues
- ERDDAP servers occasionally return 500/404 errors (external issue)
- Solution: Use climatology fallback (current approach)

## File Cleanup Summary

### Deleted Files
- Old deployment packages: `site 2/`, `deploy_package/`, `site-for-vercel.zip`
- Redundant docs: `DEPLOY.md`, `DEPLOYMENT.md`, `README_API.md`, etc.
- Test files: `test_api.py`, `api_server.py`, `test.html`, etc.
- Backup files: `index_backup.html`, `fetch_static.py.backup`, etc.

### Retained Files
- Core scripts: `step1-5.sh`, all production Python scripts
- Essential data: `forecast_year.json`, `forecast_detailed.json`
- Configuration: `.env.example`, `blueglow.code-workspace`
- Documentation: This overview, PPT outline, project structure

## Performance Metrics

### Data Processing
- Climatology calculation: ~1 second
- Astronomy calculation: ~0.5 seconds
- Model training: ~2 seconds (5000 samples)
- 7-day forecast: <1 second

### Website
- Page load: <500ms (cached)
- JSON load: <100ms (25KB forecast.json)
- Offline: Works fully offline after first visit

## Support and Resources

### Documentation
- `PROJECT_OVERVIEW.md`: This file
- `PPT_OUTLINE.md`: 18-slide presentation structure
- `config/.env.example`: Configuration template

### Contact
- Location: La Jolla, California (32.85°N, 117.27°W)
- Data Sources: NDBC, Open-Meteo, Astral library

### References
- NDBC Station 46254: https://www.ndbc.noaa.gov/station_page.php?station=46254
- Bioluminescence Info: Dinoflagellates (Lingulodinium polyedrum)

---

**Version**: 1.0-climatology
**Last Updated**: 2025-11-26
**Status**: Production Ready
