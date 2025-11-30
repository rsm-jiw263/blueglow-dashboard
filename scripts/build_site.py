#!/usr/bin/env python3
"""
Build the static website from forecast data
"""
import json
import os
from datetime import datetime


def load_forecast_data():
    """Load forecast data from JSON file"""
    try:
        with open('data/forecast.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Forecast data not found. Run Step 1 first.")
        return None


def build_html(forecast_data):
    """Build the HTML page"""
    
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueGlow 天气预测助手</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header>
        <h1>🌌 BlueGlow 天气预测助手</h1>
        <p class="subtitle">7天蓝光指数预报</p>
    </header>
    
    <main class="container">
        <section class="info-box">
            <h2>📍 位置</h2>
            <p>{location}</p>
            <p class="timestamp">更新时间: {timestamp}</p>
        </section>
        
        <section class="forecast-grid">
""".format(
        location=forecast_data.get('location', 'Unknown'),
        timestamp=datetime.fromisoformat(forecast_data['generated_at']).strftime('%Y-%m-%d %H:%M')
    )
    
    # Add forecast cards
    for day in forecast_data['forecast']:
        quality_class = day['quality'].lower()
        html += f"""
            <div class="forecast-card quality-{quality_class}">
                <h3>{day['day_name']}</h3>
                <p class="date">{day['date']}</p>
                <div class="blueglow-index">
                    <span class="index-value">{day['blueglow_index']}</span>
                    <span class="index-label">BlueGlow 指数</span>
                </div>
                <p class="quality">{day['quality']}</p>
                <div class="details">
                    <p>☁️ 云量: {day['cloud_cover']}%</p>
                    <p>👁️ 能见度: {day['visibility']} km</p>
                    <p>🌙 月相: {day['moon_phase']}%</p>
                </div>
            </div>
"""
    
    html += """
        </section>
        
        <section class="legend">
            <h2>📊 指数说明</h2>
            <div class="legend-items">
                <div class="legend-item">
                    <span class="legend-badge quality-excellent">优秀</span>
                    <span>7-10: 极佳的观测条件</span>
                </div>
                <div class="legend-item">
                    <span class="legend-badge quality-good">良好</span>
                    <span>5-7: 适合观测</span>
                </div>
                <div class="legend-item">
                    <span class="legend-badge quality-fair">一般</span>
                    <span>3-5: 可以尝试</span>
                </div>
                <div class="legend-item">
                    <span class="legend-badge quality-poor">较差</span>
                    <span>0-3: 不建议观测</span>
                </div>
            </div>
        </section>
    </main>
    
    <footer>
        <p>© 2025 BlueGlow Helper | 仅供参考</p>
    </footer>
    
    <script src="assets/js/main.js"></script>
</body>
</html>
"""
    
    return html


def build_css():
    """Build the CSS stylesheet"""
    
    css = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

header {
    text-align: center;
    color: white;
    margin-bottom: 40px;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 1.2em;
    opacity: 0.9;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.info-box {
    background: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.info-box h2 {
    color: #667eea;
    margin-bottom: 10px;
}

.timestamp {
    color: #666;
    font-size: 0.9em;
    margin-top: 10px;
}

.forecast-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.forecast-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.forecast-card:hover {
    transform: translateY(-5px);
}

.forecast-card h3 {
    color: #333;
    margin-bottom: 5px;
}

.date {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 15px;
}

.blueglow-index {
    text-align: center;
    margin: 20px 0;
}

.index-value {
    display: block;
    font-size: 3em;
    font-weight: bold;
    color: #667eea;
}

.index-label {
    display: block;
    font-size: 0.9em;
    color: #666;
}

.quality {
    text-align: center;
    font-size: 1.2em;
    font-weight: bold;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 15px;
}

.quality-excellent .quality {
    background: #4caf50;
    color: white;
}

.quality-good .quality {
    background: #8bc34a;
    color: white;
}

.quality-fair .quality {
    background: #ffc107;
    color: #333;
}

.quality-poor .quality {
    background: #f44336;
    color: white;
}

.details {
    border-top: 1px solid #eee;
    padding-top: 15px;
}

.details p {
    margin: 5px 0;
    color: #666;
}

.legend {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.legend h2 {
    color: #667eea;
    margin-bottom: 15px;
}

.legend-items {
    display: grid;
    gap: 10px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 15px;
}

.legend-badge {
    padding: 5px 15px;
    border-radius: 5px;
    font-weight: bold;
    min-width: 80px;
    text-align: center;
}

.legend-badge.quality-excellent {
    background: #4caf50;
    color: white;
}

.legend-badge.quality-good {
    background: #8bc34a;
    color: white;
}

.legend-badge.quality-fair {
    background: #ffc107;
    color: #333;
}

.legend-badge.quality-poor {
    background: #f44336;
    color: white;
}

footer {
    text-align: center;
    color: white;
    margin-top: 40px;
    padding: 20px;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 2em;
    }
    
    .forecast-grid {
        grid-template-columns: 1fr;
    }
}
"""
    
    return css


def build_js():
    """Build the JavaScript file"""
    
    js = """// Main JavaScript for BlueGlow Helper

document.addEventListener('DOMContentLoaded', function() {
    console.log('BlueGlow Helper loaded');
    
    // Add animation to cards
    const cards = document.querySelectorAll('.forecast-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Add click handler for cards (optional)
    cards.forEach(card => {
        card.addEventListener('click', function() {
            this.style.transform = 'scale(1.05)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });
});
"""
    
    return js


def build_site():
    """Main function to build the site"""
    
    print("🏗️  Building website...")
    
    # Load forecast data
    forecast_data = load_forecast_data()
    if not forecast_data:
        return
    
    # Create site directories
    os.makedirs('site/assets/css', exist_ok=True)
    os.makedirs('site/assets/js', exist_ok=True)
    
    # Build HTML
    html = build_html(forecast_data)
    with open('site/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ index.html created")
    
    # Build CSS
    css = build_css()
    with open('site/assets/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("✅ style.css created")
    
    # Build JS
    js = build_js()
    with open('site/assets/js/main.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("✅ main.js created")
    
    print("")
    print("✅ Website built successfully!")
    print("📂 Files created in: site/")
    print("🌐 Run 'Site: Preview' task to view at http://localhost:5500")


if __name__ == "__main__":
    build_site()
