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
    st.pyplot(fig3)# ============================================================================
# Tab 2: 策略对比
# ============================================================================
with tab2:
    st.header("💼 运营策略对比分析")

    st.markdown("""
    我们比较了三种不同的运营策略：
    - **策略A**: 每晚都开团（基准策略）
    - **策略B**: 仅在高评分(>0.7)时开团
    - **策略C**: 仅在周末且评分>0.6时开团
    """)

    # 显示对比表格
    st.subheader("策略对比数据")

    # 格式化显示
    display_df = scenario_results.copy()
    display_df["total_revenue"] = display_df["total_revenue"].apply(lambda x: f"${x:,.0f}")
    display_df["total_profit"] = display_df["total_profit"].apply(lambda x: f"${x:,.0f}")
    display_df["avg_profit_per_night"] = display_df["avg_profit_per_night"].apply(lambda x: f"${x:,.0f}")

    st.dataframe(display_df, use_container_width=True)

    # 可视化对比
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("总利润对比")
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        colors = ['#3b82f6', '#10b981', '#f59e0b']
        bars = ax4.bar(scenario_results["scenario"],
                       scenario_results["total_profit"],
                       color=colors, alpha=0.8)
        ax4.set_ylabel("总利润 ($)", fontsize=12)
        ax4.set_title("各策略总利润对比", fontsize=14, fontweight="bold")
        ax4.grid(True, alpha=0.3, axis='y')

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontsize=10)

        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig4)

    with col2:
        st.subheader("运营天数 vs 每晚平均利润")
        fig5, ax5 = plt.subplots(figsize=(8, 6))

        # 散点图
        scatter = ax5.scatter(scenario_results["num_nights_open"],
                             scenario_results["avg_profit_per_night"],
                             s=scenario_results["total_profit"]/1000,
                             c=colors, alpha=0.6, edgecolors='black', linewidth=2)

        # 添加标签
        for idx, row in scenario_results.iterrows():
            ax5.annotate(row["scenario"],
                        (row["num_nights_open"], row["avg_profit_per_night"]),
                        fontsize=10, ha='right')

        ax5.set_xlabel("运营天数", fontsize=12)
        ax5.set_ylabel("每晚平均利润 ($)", fontsize=12)
        ax5.set_title("运营效率分析", fontsize=14, fontweight="bold")
        ax5.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig5)

    # 推荐
    best_scenario = scenario_results.loc[scenario_results["total_profit"].idxmax()]
    st.success(f"""
    ### 🎯 推荐策略

    **{best_scenario['scenario']}**

    - 💰 总利润: ${best_scenario['total_profit']:,.2f}
    - 📅 运营天数: {best_scenario['num_nights_open']:.0f} 天
    - 💵 每晚平均利润: ${best_scenario['avg_profit_per_night']:,.2f}
    """)

# ============================================================================
# Tab 3: 交互式模拟
# ============================================================================
with tab3:
    st.header("🎮 交互式策略模拟器")

    st.markdown("""
    调整下面的参数，实时查看不同策略的业务表现。这是课堂演示的**重点功能**！
    """)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("参数设置")

        # 评分阈值
        threshold = st.slider(
            "🎯 开团评分阈值",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="只有当预测评分高于此值时才开团"
        )

        # 是否仅周末
        weekend_only = st.checkbox(
            "📅 仅周末运营",
            value=False,
            help="如果选中，只在周五、周六运营"
        )

        # 定价策略
        st.markdown("---")
        base_price = st.number_input(
            "💵 基础票价 ($)",
            min_value=50,
            max_value=200,
            value=100,
            step=10
        )

        premium_multiplier = st.slider(
            "⭐ 高分加价系数",
            min_value=1.0,
            max_value=2.0,
            value=1.2,
            step=0.1,
            help="评分>0.8时的价格倍数"
        )

    with col2:
        st.subheader("模拟结果")

        # 计算模拟结果
        sim_df = env_df.copy()

        # 添加星期几
        sim_df["is_weekend"] = sim_df["date"].dt.dayofweek >= 5

        # 决定是否开团
        if weekend_only:
            sim_df["open"] = (sim_df["predicted_score"] > threshold) & sim_df["is_weekend"]
        else:
            sim_df["open"] = sim_df["predicted_score"] > threshold

        # 计算收益（简化模型）
        sim_df["price"] = np.where(
            sim_df["predicted_score"] > 0.8,
            base_price * premium_multiplier,
            base_price
        )

        # 假设客户数与评分相关
        sim_df["customers"] = np.clip(
            10 + (sim_df["predicted_score"] * 20).astype(int),
            5, 30
        )

        sim_df["revenue"] = sim_df["open"] * sim_df["price"] * sim_df["customers"]

        # 成本（简化：固定+变动）
        fixed_cost_per_night = 500
        variable_cost_per_customer = 20
        sim_df["cost"] = sim_df["open"] * (fixed_cost_per_night + variable_cost_per_customer * sim_df["customers"])
        sim_df["profit"] = sim_df["revenue"] - sim_df["cost"]

        # 关键指标
        total_nights = sim_df["open"].sum()
        total_revenue = sim_df["revenue"].sum()
        total_profit = sim_df["profit"].sum()
        avg_profit_per_night = sim_df[sim_df["open"]]["profit"].mean() if total_nights > 0 else 0

        # 显示指标卡片
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            st.metric(
                label="🗓️ 运营天数",
                value=f"{total_nights:.0f}",
                delta=f"{total_nights/365*100:.1f}% of year"
            )

        with metric_col2:
            st.metric(
                label="💰 总收入",
                value=f"${total_revenue:,.0f}"
            )

        with metric_col3:
            st.metric(
                label="💵 总利润",
                value=f"${total_profit:,.0f}"
            )

        with metric_col4:
            st.metric(
                label="📊 每晚平均利润",
                value=f"${avg_profit_per_night:,.0f}"
            )

        # 月度利润图
        st.markdown("---")
        st.subheader("月度利润趋势")

        sim_df["month"] = sim_df["date"].dt.month
        monthly_profit = sim_df.groupby("month")["profit"].sum()

        fig6, ax6 = plt.subplots(figsize=(10, 5))
        monthly_profit.plot(kind="bar", ax=ax6, color="#10b981", alpha=0.8)
        ax6.set_xlabel("月份", fontsize=12)
        ax6.set_ylabel("月度利润 ($)", fontsize=12)
        ax6.set_title(f"模拟策略月度利润 (阈值={threshold}, 周末限制={'是' if weekend_only else '否'})",
                     fontsize=13, fontweight="bold")
        ax6.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig6)

        # 开团日历视图
        st.markdown("---")
        st.subheader("开团日历（示例：前3个月）")

        # 只显示前90天
        calendar_df = sim_df.head(90).copy()
        calendar_df["day_of_month"] = calendar_df["date"].dt.day
        calendar_df["month"] = calendar_df["date"].dt.month

        # 创建热力图数据
        pivot_data = calendar_df.pivot_table(
            values="open",
            index="day_of_month",
            columns="month",
            aggfunc="sum",
            fill_value=0
        )

        fig7, ax7 = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot_data, annot=True, fmt=".0f", cmap="YlGnBu",
                   cbar_kws={'label': '是否开团'}, ax=ax7, linewidths=0.5)
        ax7.set_xlabel("月份", fontsize=12)
        ax7.set_ylabel("日期", fontsize=12)
        ax7.set_title("开团日历热力图 (前3个月)", fontsize=13, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig7)

# ============================================================================
# Tab 4: 深度分析
# ============================================================================
with tab4:
    st.header("🔍 深度数据分析")

    # 特征重要性
    st.subheader("🎯 特征重要性分析")

    col1, col2 = st.columns(2)

    with col1:
        fig8, ax8 = plt.subplots(figsize=(8, 6))
        ax8.barh(feature_importance["feature"],
                feature_importance["importance"],
                color="#6366f1", alpha=0.8)
        ax8.set_xlabel("重要性", fontsize=12)
        ax8.set_title("机器学习模型特征重要性", fontsize=13, fontweight="bold")
        ax8.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig8)

    with col2:
        st.markdown("**特征解释**:")
        for _, row in feature_importance.iterrows():
            feature_map = {
                "water_temp": "🌡️ 水温",
                "wave_height": "🌊 浪高",
                "wind_speed": "💨 风速",
                "moon_phase": "🌙 月相"
            }
            feature_name = feature_map.get(row["feature"], row["feature"])
            st.write(f"{feature_name}: **{row['importance']:.3f}**")

        st.info("""
        **解读**:
        - 水温和月相是最重要的预测因子
        - 蓝眼泪通常在温暖水温时出现
        - 新月/满月期间发生概率更高
        """)

    # 环境因素相关性
    st.markdown("---")
    st.subheader("📊 环境因素分布")

    fig9, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 水温分布
    axes[0, 0].hist(env_df["water_temp"], bins=30, color="#ef4444", alpha=0.7)
    axes[0, 0].set_xlabel("水温 (°C)")
    axes[0, 0].set_ylabel("天数")
    axes[0, 0].set_title("水温分布")
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # 浪高分布
    axes[0, 1].hist(env_df["wave_height"], bins=30, color="#3b82f6", alpha=0.7)
    axes[0, 1].set_xlabel("浪高 (m)")
    axes[0, 1].set_ylabel("天数")
    axes[0, 1].set_title("浪高分布")
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 风速分布
    axes[1, 0].hist(env_df["wind_speed"], bins=30, color="#10b981", alpha=0.7)
    axes[1, 0].set_xlabel("风速 (m/s)")
    axes[1, 0].set_ylabel("天数")
    axes[1, 0].set_title("风速分布")
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 月相分布
    axes[1, 1].hist(env_df["moon_phase"], bins=30, color="#f59e0b", alpha=0.7)
    axes[1, 1].set_xlabel("月相 (0=新月, 1=满月)")
    axes[1, 1].set_ylabel("天数")
    axes[1, 1].set_title("月相分布")
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    st.pyplot(fig9)

    # 交易数据分析
    st.markdown("---")
    st.subheader("💳 交易数据分析")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_transactions = len(transactions_df)
        st.metric("总交易数", f"{total_transactions}")

    with col2:
        total_customers = transactions_df["num_customers"].sum()
        st.metric("总客户数", f"{total_customers:,}")

    with col3:
        avg_price = transactions_df["price_per_person"].mean()
        st.metric("平均票价", f"${avg_price:.2f}")

    # 产品类型分布
    st.subheader("产品类型分布")

    product_summary = transactions_df.groupby("product_type").agg({
        "revenue": "sum",
        "profit": "sum",
        "num_customers": "sum"
    }).reset_index()

    fig10, ax10 = plt.subplots(figsize=(10, 6))
    x = np.arange(len(product_summary))
    width = 0.35

    ax10.bar(x - width/2, product_summary["revenue"], width, label='收入', alpha=0.8)
    ax10.bar(x + width/2, product_summary["profit"], width, label='利润', alpha=0.8)

    ax10.set_xlabel("产品类型")
    ax10.set_ylabel("金额 ($)")
    ax10.set_title("各产品类型收入与利润对比")
    ax10.set_xticks(x)
    ax10.set_xticklabels(product_summary["product_type"])
    ax10.legend()
    ax10.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig10)

# ============================================================================
# Tab 5: 商业建议
# ============================================================================
with tab5:
    st.header("🎯 商业建议与行动计划")

    st.markdown("""
    基于数据分析和模型预测，我们提出以下商业建议：
    """)

    # 关键发现
    st.subheader("📌 关键发现")

    col1, col2 = st.columns(2)

    with col1:
        st.success("""
        ### ✅ 优势

        1. **高质量天数充足**: 全年有 84 天评分>0.65 (23%)
        2. **优秀天数可观**: 55 天评分>0.667 (Top 15%)
        3. **季节性明显**: 4-8月为最佳季节
        4. **市场需求**: La Jolla地区旅游业发达
        5. **独特体验**: 蓝眼泪是罕见自然奇观
        """)

    with col2:
        st.warning("""
        ### ⚠️ 挑战

        1. **天气依赖**: 受环境因素影响大
        2. **不可预测**: 100%准确预测困难
        3. **季节性收入**: 淡旺季差异明显
        4. **运营成本**: 需要专业导游和设备
        """)

    # 推荐策略
    st.markdown("---")
    st.subheader("🚀 推荐运营策略")

    st.info("""
    ### 混合策略（推荐）

    **阶段1: 试运营（前3个月）**
    - 仅在评分>0.667时开团（优秀天数，降低风险）
    - 周末优先运营
    - 小规模团队（10-15人/团）
    - 收集客户反馈

    **阶段2: 扩展期（4-9月）**
    - 降低阈值至0.65（高质量天数，扩大运营）
    - 增加周中团次
    - 扩大团队规模（20-25人/团）
    - 开发高端产品线

    **阶段3: 优化期（10-12月）**
    - 根据历史数据调整阈值
    - 动态定价策略
    - 会员/常客计划
    - 冬季淡季促销
    """)

    # 财务预测
    st.markdown("---")
    st.subheader("💰 财务预测（第一年）")

    # 使用最佳策略的数字
    best_profit = scenario_results["total_profit"].max()
    best_revenue = scenario_results.loc[scenario_results["total_profit"].idxmax(), "total_revenue"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("预计收入", f"${best_revenue:,.0f}")

    with col2:
        st.metric("预计利润", f"${best_profit:,.0f}")

    with col3:
        profit_margin = (best_profit / best_revenue * 100) if best_revenue > 0 else 0
        st.metric("利润率", f"{profit_margin:.1f}%")

    with col4:
        breakeven_months = 3  # 估计
        st.metric("预计回本周期", f"{breakeven_months} 个月")

    # 风险管理
    st.markdown("---")
    st.subheader("🛡️ 风险管理")

    st.markdown("""
    **主要风险与应对措施**:

    | 风险 | 概率 | 影响 | 应对措施 |
    |------|------|------|----------|
    | 天气恶劣导致取消 | 中 | 高 | 灵活退款政策，保险 |
    | 蓝眼泪未出现 | 中 | 中 | 设置合理预期，备选活动 |
    | 竞争对手进入 | 低 | 中 | 建立品牌，优质服务 |
    | 环境政策变化 | 低 | 高 | 遵守规定，环保运营 |
    """)

    # 下一步行动
    st.markdown("---")
    st.subheader("📋 下一步行动计划")

    st.markdown("""
    ### 立即行动（1-3个月）

    - [ ] 完成市场调研和竞争分析
    - [ ] 申请必要的运营许可证
    - [ ] 购买/租赁必要设备（船只、安全设备）
    - [ ] 招聘和培训导游团队
    - [ ] 开发预订系统和网站
    - [ ] 建立社交媒体营销

    ### 中期目标（3-6个月）

    - [ ] 开始试运营
    - [ ] 收集客户反馈并优化
    - [ ] 建立合作伙伴关系（酒店、旅行社）
    - [ ] 优化定价策略
    - [ ] 扩大市场推广

    ### 长期愿景（6-12个月）

    - [ ] 扩展产品线（摄影团、私人包船）
    - [ ] 开发周边商品
    - [ ] 建立会员计划
    - [ ] 探索其他地点可能性
    - [ ] 实现盈利并计划扩张
    """)

    # 联系信息
    st.markdown("---")
    st.success("""
    ### 📞 项目团队

    **MGTA 452 Final Project**

    感谢您查看我们的可行性分析！如有任何问题或建议，欢迎联系。

    *数据来源: NOAA, NDBC, 历史观测记录*
    *模型: Random Forest Classifier & Regressor*
    *工具: Python, Pandas, Scikit-learn, Streamlit*
    """)

# ============================================================================
# 底部信息
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p>🌊 La Jolla Blue Tears Feasibility Dashboard</p>
    <p>MGTA 452 Business Analytics | 2024</p>
    <p>Powered by Streamlit 🚀</p>
</div>
""", unsafe_allow_html=True)
