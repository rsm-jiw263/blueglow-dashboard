"""
La Jolla Blue Tears - Interactive Feasibility Dashboard
MGTA 452 Final Project
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="La Jolla Blue Tears Dashboard",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #0f172a;
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        font-weight: 400;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stMetric label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.875rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #0f172a;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        padding: 12px 24px;
        border-radius: 8px 8px 0 0;
    }
    
    .stMarkdown {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load all required datasets"""
    try:
        env_df = pd.read_csv("streamlit_data/env_df_for_app.csv", parse_dates=["date"])
        scenario_results = pd.read_csv("streamlit_data/scenario_results.csv")
        transactions_df = pd.read_csv("streamlit_data/transactions_df.csv", parse_dates=["date"])
        feature_importance = pd.read_csv("streamlit_data/feature_importance.csv")
        
        # Try to load classification data (may not exist)
        try:
            classification_data = pd.read_csv("streamlit_data/classification_data.csv", parse_dates=["date"])
        except:
            classification_data = None
        
        return env_df, scenario_results, transactions_df, feature_importance, classification_data
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}")
        st.info("Please run the data export cell in the notebook first!")
        st.stop()

# Load data
env_df, scenario_results, transactions_df, feature_importance, classification_data = load_data()

# Ensure predicted_score column exists
if "predicted_score" not in env_df.columns:
    env_df["predicted_score"] = env_df.get("blue_tears_score", 0.5)

# ============================================================================
# Page Header
# ============================================================================
st.markdown('<h1 class="main-header">La Jolla Blue Tears Feasibility Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">MGTA 452 Final Project – Interactive Dashboard</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# Sidebar - Project Overview
# ============================================================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400", use_container_width=True)
    st.markdown("## Project Overview")
    st.markdown("""
    **Objective**: Evaluate commercial feasibility of La Jolla blue tears night tour service
    
    **Data Sources**:
    - Water temperature and wind speed (NOAA)
    - Wave height data (NDBC buoy)
    - Astronomical moon phase calculations
    - 2020 red tide event labels
    
    **Methodology**:
    - Machine learning prediction models
    - Business scenario simulation
    - Revenue optimization strategies
    """)
    
    st.markdown("---")
    st.markdown("**Dataset Statistics**")
    st.metric("Environmental Data", f"{len(env_df)} days")
    st.metric("Transaction Records", f"{len(transactions_df)} records")
    st.metric("Prediction Model", "RandomForest")

# ============================================================================
# Tab Layout
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Seasonality Analysis", 
    "Strategy Comparison", 
    "Interactive Simulator", 
    "Deep Dive Analytics",
    "Business Recommendations"
])

# ============================================================================
# Tab 1: Seasonality Analysis
# ============================================================================
with tab1:
    st.header("Blue Tears Score Seasonality Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_score = env_df["predicted_score"].mean()
        st.metric("Average Score", f"{avg_score:.3f}", help="Annual average blue tears occurrence probability")
    
    with col2:
        high_quality_days = (env_df["predicted_score"] > 0.65).sum()
        st.metric("High Quality Days", f"{high_quality_days} days", 
                  delta=f"{high_quality_days/len(env_df)*100:.1f}% of year",
                  help="Days with score > 0.65 (Top 25%)")
    
    with col3:
        excellent_days = (env_df["predicted_score"] > 0.667).sum()
        st.metric("Excellent Days", f"{excellent_days} days",
                  delta=f"{excellent_days/len(env_df)*100:.1f}%",
                  help="Days with score > 0.667 (Top 15%)")
    
    st.markdown("---")
    
    # Monthly trend charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Monthly Average Score")
        env_df["month"] = env_df["date"].dt.month
        monthly_mean = env_df.groupby("month")["predicted_score"].mean()
        
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        monthly_mean.plot(kind="bar", ax=ax1, color="#3b82f6", alpha=0.8)
        ax1.axhline(y=0.65, color='orange', linestyle='--', label='High Quality (0.65)', alpha=0.6)
        ax1.axhline(y=0.667, color='red', linestyle='--', label='Excellent (0.667)', alpha=0.6)
        ax1.set_xlabel("Month", fontsize=12)
        ax1.set_ylabel("Average Score (0-1)", fontsize=12)
        ax1.set_title("Monthly Average Blue Tears Score", fontsize=14, fontweight="bold")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig1)
        
        st.info(f"**Best Month**: Month {monthly_mean.idxmax()} (Score: {monthly_mean.max():.3f})")
    
    with col_right:
        st.subheader("Annual Time Series")
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(env_df["date"], env_df["predicted_score"], linewidth=1.5, alpha=0.8)
        ax2.axhline(y=0.65, color='orange', linestyle='--', label='High Quality (0.65)', alpha=0.6)
        ax2.axhline(y=0.667, color='red', linestyle='--', label='Excellent (0.667)', alpha=0.6)
        ax2.fill_between(env_df["date"], 0, env_df["predicted_score"], 
                          where=(env_df["predicted_score"] > 0.65),
                          alpha=0.3, color='green', label='High Quality Days')
        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("Score", fontsize=12)
        ax2.set_title("2024 Blue Tears Score Time Series", fontsize=14, fontweight="bold")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)
    
    # Score distribution
    st.subheader("Score Distribution Histogram")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.hist(env_df["predicted_score"], bins=30, color="#3b82f6", alpha=0.7, edgecolor='black')
    ax3.axvline(x=0.65, color='orange', linestyle='--', linewidth=2, label='High Quality = 0.65')
    ax3.axvline(x=0.667, color='red', linestyle='--', linewidth=2, label='Excellent = 0.667')
    ax3.set_xlabel("Blue Tears Score", fontsize=12)
    ax3.set_ylabel("Number of Days", fontsize=12)
    ax3.set_title("Score Distribution", fontsize=14, fontweight="bold")
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig3)

# ============================================================================
# Tab 2: Strategy Comparison
# ============================================================================
with tab2:
    st.header("Operating Strategy Comparison Analysis")
    
    st.markdown("""
    We compare three different operating strategies:
    - **Strategy A**: Open tours every night (baseline strategy)
    - **Strategy B**: Open only when high score (>0.7)
    - **Strategy C**: Open only on weekends with score >0.6
    """)
    
    # Display comparison table
    st.subheader("Strategy Comparison Data")
    
    # Format display
    display_df = scenario_results.copy()
    display_df["total_revenue"] = display_df["total_revenue"].apply(lambda x: f"${x:,.0f}")
    display_df["total_profit"] = display_df["total_profit"].apply(lambda x: f"${x:,.0f}")
    display_df["avg_profit_per_night"] = display_df["avg_profit_per_night"].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Visualization comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Profit Comparison")
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        colors = ['#3b82f6', '#10b981', '#f59e0b']
        bars = ax4.bar(scenario_results["scenario"], 
                       scenario_results["total_profit"], 
                       color=colors, alpha=0.8)
        ax4.set_ylabel("Total Profit ($)", fontsize=12)
        ax4.set_title("Total Profit by Strategy", fontsize=14, fontweight="bold")
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig4)
    
    with col2:
        st.subheader("Operating Days vs Avg Profit per Night")
        fig5, ax5 = plt.subplots(figsize=(8, 6))
        
        # Scatter plot
        scatter = ax5.scatter(scenario_results["num_nights_open"], 
                             scenario_results["avg_profit_per_night"],
                             s=scenario_results["total_profit"]/1000,
                             c=colors, alpha=0.6, edgecolors='black', linewidth=2)
        
        # Add labels
        for idx, row in scenario_results.iterrows():
            ax5.annotate(row["scenario"], 
                        (row["num_nights_open"], row["avg_profit_per_night"]),
                        fontsize=10, ha='right')
        
        ax5.set_xlabel("Operating Days", fontsize=12)
        ax5.set_ylabel("Avg Profit per Night ($)", fontsize=12)
        ax5.set_title("Operating Efficiency Analysis", fontsize=14, fontweight="bold")
        ax5.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig5)
    
    # Recommendation
    best_scenario = scenario_results.loc[scenario_results["total_profit"].idxmax()]
    st.success(f"""
    ### Recommended Strategy
    
    **{best_scenario['scenario']}** 
    
    - Total Profit: ${best_scenario['total_profit']:,.2f}
    - Operating Days: {best_scenario['num_nights_open']:.0f} days
    - Avg Profit per Night: ${best_scenario['avg_profit_per_night']:,.2f}
    """)

# ============================================================================
# Tab 3: Interactive Simulator
# ============================================================================
with tab3:
    st.header("Interactive Strategy Simulator")
    
    st.markdown("""
    Adjust the parameters below to see real-time business performance under different strategies. 
    This is the **key feature** for classroom demonstrations!
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameter Settings")
        
        # Score threshold
        threshold = st.slider(
            "Score Threshold for Opening Tours",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Tours will only open when predicted score exceeds this threshold"
        )
        
        # Weekend only
        weekend_only = st.checkbox(
            "Weekend Operations Only",
            value=False,
            help="If checked, only operate on Fridays and Saturdays"
        )
        
        # Pricing strategy
        st.markdown("---")
        base_price = st.number_input(
            "Base Ticket Price ($)",
            min_value=50,
            max_value=200,
            value=100,
            step=10
        )
        
        premium_multiplier = st.slider(
            "Premium Price Multiplier",
            min_value=1.0,
            max_value=2.0,
            value=1.2,
            step=0.1,
            help="Price multiplier for high-score days (>0.8)"
        )
        
    with col2:
        st.subheader("Simulation Results")
        
        # Calculate simulation results
        sim_df = env_df.copy()
        
        # Add day of week
        sim_df["is_weekend"] = sim_df["date"].dt.dayofweek >= 5
        
        # Decide whether to open
        if weekend_only:
            sim_df["open"] = (sim_df["predicted_score"] > threshold) & sim_df["is_weekend"]
        else:
            sim_df["open"] = sim_df["predicted_score"] > threshold
        
        # Calculate revenue (simplified model)
        sim_df["price"] = np.where(
            sim_df["predicted_score"] > 0.8,
            base_price * premium_multiplier,
            base_price
        )
        
        # Assume customer count correlates with score
        sim_df["customers"] = np.clip(
            10 + (sim_df["predicted_score"] * 20).astype(int),
            5, 30
        )
        
        sim_df["revenue"] = sim_df["open"] * sim_df["price"] * sim_df["customers"]
        
        # Costs (simplified: fixed + variable)
        fixed_cost_per_night = 500
        variable_cost_per_customer = 20
        sim_df["cost"] = sim_df["open"] * (fixed_cost_per_night + variable_cost_per_customer * sim_df["customers"])
        sim_df["profit"] = sim_df["revenue"] - sim_df["cost"]
        
        # Key metrics
        total_nights = sim_df["open"].sum()
        total_revenue = sim_df["revenue"].sum()
        total_profit = sim_df["profit"].sum()
        avg_profit_per_night = sim_df[sim_df["open"]]["profit"].mean() if total_nights > 0 else 0
        
        # Display metric cards
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric(
                label="Operating Days",
                value=f"{total_nights:.0f}",
                delta=f"{total_nights/365*100:.1f}% of year"
            )
        
        with metric_col2:
            st.metric(
                label="Total Revenue",
                value=f"${total_revenue:,.0f}"
            )
        
        with metric_col3:
            st.metric(
                label="Total Profit",
                value=f"${total_profit:,.0f}"
            )
        
        with metric_col4:
            st.metric(
                label="Avg Profit per Night",
                value=f"${avg_profit_per_night:,.0f}"
            )
        
        # Monthly profit chart
        st.markdown("---")
        st.subheader("Monthly Profit Trend")
        
        sim_df["month"] = sim_df["date"].dt.month
        monthly_profit = sim_df.groupby("month")["profit"].sum()
        
        fig6, ax6 = plt.subplots(figsize=(10, 5))
        monthly_profit.plot(kind="bar", ax=ax6, color="#10b981", alpha=0.8)
        ax6.set_xlabel("Month", fontsize=12)
        ax6.set_ylabel("Monthly Profit ($)", fontsize=12)
        ax6.set_title(f"Simulated Monthly Profit (Threshold={threshold}, Weekend Only={'Yes' if weekend_only else 'No'})", 
                     fontsize=13, fontweight="bold")
        ax6.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig6)
        
        # Operating calendar heatmap
        st.markdown("---")
        st.subheader("Operating Calendar (First 3 Months)")
        
        # Show only first 90 days
        calendar_df = sim_df.head(90).copy()
        calendar_df["day_of_month"] = calendar_df["date"].dt.day
        calendar_df["month"] = calendar_df["date"].dt.month
        
        # Create heatmap data
        pivot_data = calendar_df.pivot_table(
            values="open",
            index="day_of_month",
            columns="month",
            aggfunc="sum",
            fill_value=0
        )
        
        fig7, ax7 = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot_data, annot=True, fmt=".0f", cmap="YlGnBu", 
                   cbar_kws={'label': 'Open (1) or Closed (0)'}, ax=ax7, linewidths=0.5)
        ax7.set_xlabel("Month", fontsize=12)
        ax7.set_ylabel("Day of Month", fontsize=12)
        ax7.set_title("Operating Calendar Heatmap (First 3 Months)", fontsize=13, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig7)

# ============================================================================
# Tab 4: Deep Dive Analytics
# ============================================================================
with tab4:
    st.header("Deep Dive Data Analytics")
    
    # Feature importance
    st.subheader("Feature Importance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig8, ax8 = plt.subplots(figsize=(8, 6))
        ax8.barh(feature_importance["feature"], 
                feature_importance["importance"],
                color="#6366f1", alpha=0.8)
        ax8.set_xlabel("Importance", fontsize=12)
        ax8.set_title("Machine Learning Model Feature Importance", fontsize=13, fontweight="bold")
        ax8.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig8)
    
    with col2:
        st.markdown("**Feature Interpretation**:")
        feature_map = {
            "water_temp": "Water Temperature",
            "wave_height": "Wave Height",
            "wind_speed": "Wind Speed",
            "moon_phase": "Moon Phase"
        }
        for _, row in feature_importance.iterrows():
            feature_name = feature_map.get(row["feature"], row["feature"])
            st.write(f"{feature_name}: **{row['importance']:.3f}**")
        
        st.info("""
        **Interpretation**:
        - Water temperature and moon phase are the most important predictors
        - Blue tears typically occur in warmer water
        - Higher probability during new moon/full moon periods
        """)
    
    # Environmental factor correlation
    st.markdown("---")
    st.subheader("Environmental Factor Distributions")
    
    fig9, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Water temperature distribution
    axes[0, 0].hist(env_df["water_temp"], bins=30, color="#ef4444", alpha=0.7)
    axes[0, 0].set_xlabel("Water Temperature (°C)")
    axes[0, 0].set_ylabel("Number of Days")
    axes[0, 0].set_title("Water Temperature Distribution")
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # Wave height distribution
    axes[0, 1].hist(env_df["wave_height"], bins=30, color="#3b82f6", alpha=0.7)
    axes[0, 1].set_xlabel("Wave Height (m)")
    axes[0, 1].set_ylabel("Number of Days")
    axes[0, 1].set_title("Wave Height Distribution")
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Wind speed distribution
    axes[1, 0].hist(env_df["wind_speed"], bins=30, color="#10b981", alpha=0.7)
    axes[1, 0].set_xlabel("Wind Speed (m/s)")
    axes[1, 0].set_ylabel("Number of Days")
    axes[1, 0].set_title("Wind Speed Distribution")
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Moon phase distribution
    axes[1, 1].hist(env_df["moon_phase"], bins=30, color="#f59e0b", alpha=0.7)
    axes[1, 1].set_xlabel("Moon Phase (0=New Moon, 1=Full Moon)")
    axes[1, 1].set_ylabel("Number of Days")
    axes[1, 1].set_title("Moon Phase Distribution")
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    st.pyplot(fig9)
    
    # Transaction data analysis
    st.markdown("---")
    st.subheader("Transaction Data Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_transactions = len(transactions_df)
        st.metric("Total Transactions", f"{total_transactions}")
    
    with col2:
        total_customers = transactions_df["num_customers"].sum()
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col3:
        avg_price = transactions_df["price_per_person"].mean()
        st.metric("Average Ticket Price", f"${avg_price:.2f}")
    
    # Product type distribution
    st.subheader("Product Type Distribution")
    
    product_summary = transactions_df.groupby("product_type").agg({
        "revenue": "sum",
        "profit": "sum",
        "num_customers": "sum"
    }).reset_index()
    
    fig10, ax10 = plt.subplots(figsize=(10, 6))
    x = np.arange(len(product_summary))
    width = 0.35
    
    ax10.bar(x - width/2, product_summary["revenue"], width, label='Revenue', alpha=0.8)
    ax10.bar(x + width/2, product_summary["profit"], width, label='Profit', alpha=0.8)
    
    ax10.set_xlabel("Product Type")
    ax10.set_ylabel("Amount ($)")
    ax10.set_title("Revenue vs Profit by Product Type")
    ax10.set_xticks(x)
    ax10.set_xticklabels(product_summary["product_type"])
    ax10.legend()
    ax10.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig10)

# ============================================================================
# Tab 5: Business Recommendations
# ============================================================================
with tab5:
    st.header("Business Recommendations & Action Plan")
    
    st.markdown("""
    Based on data analysis and model predictions, we present the following business recommendations:
    """)
    
    # Key findings
    st.subheader("Key Findings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        ### Strengths
        
        1. **Sufficient High-Quality Days**: 84 days with score >0.65 (23%)
        2. **Notable Excellent Days**: 55 days with score >0.667 (Top 15%)
        3. **Clear Seasonality**: April-August are optimal months
        4. **Market Demand**: La Jolla region has strong tourism industry
        5. **Unique Experience**: Blue tears are a rare natural phenomenon
        """)
    
    with col2:
        st.warning("""
        ### Challenges
        
        1. **Weather Dependency**: Heavily influenced by environmental factors
        2. **Unpredictability**: 100% accurate prediction is difficult
        3. **Seasonal Revenue**: Significant variation between peak and off-peak seasons
        4. **Operating Costs**: Requires professional guides and equipment
        """)
    
    # Recommended strategy
    st.markdown("---")
    st.subheader("Recommended Operating Strategy")
    
    st.info("""
    ### Hybrid Strategy (Recommended)
    
    **Phase 1: Pilot Operations (First 3 Months)**
    - Open tours only when score >0.667 (excellent days, minimize risk)
    - Prioritize weekend operations
    - Small team size (10-15 people per tour)
    - Collect customer feedback
    
    **Phase 2: Expansion Period (Months 4-9)**
    - Lower threshold to 0.65 (high-quality days, expand operations)
    - Increase weekday tour frequency
    - Expand team size (20-25 people per tour)
    - Develop premium product lines
    
    **Phase 3: Optimization Period (Months 10-12)**
    - Adjust thresholds based on historical data
    - Implement dynamic pricing strategy
    - Launch membership/loyalty programs
    - Winter off-season promotions
    """)
    
    # Financial projections
    st.markdown("---")
    st.subheader("Financial Projections (First Year)")
    
    # Use best strategy numbers
    best_profit = scenario_results["total_profit"].max()
    best_revenue = scenario_results.loc[scenario_results["total_profit"].idxmax(), "total_revenue"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Projected Revenue", f"${best_revenue:,.0f}")
    
    with col2:
        st.metric("Projected Profit", f"${best_profit:,.0f}")
    
    with col3:
        profit_margin = (best_profit / best_revenue * 100) if best_revenue > 0 else 0
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    with col4:
        breakeven_months = 3  # estimate
        st.metric("Breakeven Period", f"{breakeven_months} months")
    
    # Risk management
    st.markdown("---")
    st.subheader("Risk Management")
    
    st.markdown("""
    **Key Risks and Mitigation Measures**:
    
    | Risk | Probability | Impact | Mitigation Measures |
    |------|------------|--------|---------------------|
    | Severe weather cancellations | Medium | High | Flexible refund policy, insurance |
    | Blue tears no-show | Medium | Medium | Set realistic expectations, backup activities |
    | Competitor entry | Low | Medium | Build brand, premium service |
    | Environmental policy changes | Low | High | Comply with regulations, eco-friendly operations |
    """)
    
    # Next steps action plan
    st.markdown("---")
    st.subheader("Action Plan")
    
    st.markdown("""
    ### Immediate Actions (1-3 Months)
    
    - Complete market research and competitive analysis
    - Apply for necessary operating permits
    - Purchase/lease required equipment (boats, safety gear)
    - Recruit and train tour guide team
    - Develop booking system and website
    - Establish social media marketing presence
    
    ### Medium-Term Goals (3-6 Months)
    
    - Begin pilot operations
    - Collect customer feedback and optimize
    - Establish partnerships (hotels, travel agencies)
    - Optimize pricing strategy
    - Expand marketing efforts
    
    ### Long-Term Vision (6-12 Months)
    
    - Expand product line (photography tours, private charters)
    - Develop merchandise
    - Launch membership program
    - Explore additional locations
    - Achieve profitability and plan for expansion
    """)
    
    # Contact information
    st.markdown("---")
    st.success("""
    ### Project Team
    
    **MGTA 452 Final Project**  
    
    Thank you for reviewing our feasibility analysis! Please feel free to reach out with any questions or suggestions.
    
    *Data Sources: NOAA, NDBC, Historical Observation Records*  
    *Models: Random Forest Classifier & Regressor*  
    *Tools: Python, Pandas, Scikit-learn, Streamlit*
    """)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p>La Jolla Blue Tears Feasibility Dashboard</p>
    <p>MGTA 452 Business Analytics | 2024</p>
    <p>Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)
