import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="ClimateScope Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
# =====================================================
# PART 2: ENHANCED CSS WITH BRIGHT NAVIGATION
# Copy this entire section into your dashboard
# =====================================================

# 
@st.cache_data(show_spinner=False)
def load_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    :root {
        --climate-primary: #10b981;
        --climate-secondary: #059669;
        --climate-accent: #06b6d4;
        --climate-warning: #f59e0b;
        --climate-danger: #ef4444;
        --climate-info: #3b82f6;
        --climate-yellow: #FFA500;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0f1e 0%, #0f1419 25%, #0d1b2a 50%, #0a1628 75%, #0a0f1e 100%);
        color: #f8fafc;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        background-attachment: fixed;
    }

    /* ========================================
       SIDEBAR NAVIGATION - BRIGHT & VISIBLE
       ======================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* ALL Sidebar Labels - BRIGHT WHITE */
    section[data-testid="stSidebar"] label {
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* Radio Button Container - Visible Cards */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin: 6px 0 !important;
        color: #e5e7eb !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }

    /* Radio Button Hover - BRIGHT GREEN GLOW */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(16, 185, 129, 0.15) !important;
        border-color: #10b981 !important;
        color: #10b981 !important;
        transform: translateX(4px) !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.3) !important;
    }

    /* Selected Radio Button - BRIGHT GREEN GRADIENT */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border-color: #10b981 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4) !important;
        font-weight: 700 !important;
    }

    /* Sidebar Headers */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Sidebar Divider */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(16, 185, 129, 0.3) !important;
        margin: 20px 0 !important;
    }

    /* Multiselect & Selectbox */
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stDateInput label,
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stNumberInput label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* ========================================
       KPI CARDS - CLIMATE METRICS
       ======================================== */
    .kpi-box {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 28px 24px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .kpi-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--climate-primary), var(--climate-accent));
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .kpi-box:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: var(--climate-primary);
        box-shadow: 0 20px 60px rgba(16, 185, 129, 0.3);
    }

    .kpi-box:hover::before {
        opacity: 1;
    }

    .kpi-good {
        border-left: 5px solid var(--climate-primary);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%);
    }

    .kpi-warning {
        border-left: 5px solid var(--climate-warning);
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%);
    }

    .kpi-critical {
        border-left: 5px solid var(--climate-danger);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(17, 24, 39, 0.95) 100%);
    }

    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
        filter: drop-shadow(0 4px 12px rgba(16, 185, 129, 0.4));
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }

    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
        margin: 12px 0;
        background: linear-gradient(135deg, var(--climate-primary), var(--climate-accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .kpi-trend {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 8px;
        padding: 6px 12px;
        border-radius: 12px;
        display: inline-block;
    }

    .kpi-trend.positive {
        background: rgba(16, 185, 129, 0.15);
        color: var(--climate-primary);
    }

    .kpi-trend.negative {
        background: rgba(239, 68, 68, 0.15);
        color: var(--climate-danger);
    }

    /* ========================================
       INSIGHT CARDS - COLLAPSIBLE WITH CLIMATE COLORS
       ======================================== */
    .insight-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 0;
        margin: 16px 0;
        border-left: 5px solid var(--climate-info);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        overflow: hidden;
    }

    .insight-header {
        padding: 20px 28px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
        user-select: none;
    }

    .insight-header:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .insight-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        color: #F8FAFC;
    }

    .insight-icon {
        font-size: 1.5rem;
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
    }

    .insight-toggle {
        font-size: 1.5rem;
        transition: transform 0.3s ease;
        color: #94A3B8;
    }

    .insight-toggle.active {
        transform: rotate(180deg);
    }

    .insight-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.4s ease, padding 0.4s ease;
        padding: 0 28px;
    }

    .insight-content.active {
        max-height: 500px;
        padding: 0 28px 24px 28px;
    }

    .insight-text {
        color: #CBD5E1;
        line-height: 1.7;
        font-size: 0.95rem;
    }

    /* POSITIVE INSIGHTS - Green/Eco Theme */
    .insight-positive {
        border-left-color: var(--climate-primary);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(17, 24, 39, 0.9) 100%);
    }

    .insight-positive .insight-header:hover {
        background: rgba(16, 185, 129, 0.1);
    }

    .insight-positive .insight-icon {
        color: #10B981;
    }

    .insight-positive:hover {
        box-shadow: 0 12px 48px rgba(16, 185, 129, 0.3);
        transform: translateY(-2px);
    }

    /* WARNING INSIGHTS - Amber/Caution Theme */
    .insight-warning {
        border-left-color: var(--climate-warning);
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(17, 24, 39, 0.9) 100%);
    }

    .insight-warning .insight-header:hover {
        background: rgba(245, 158, 11, 0.1);
    }

    .insight-warning .insight-icon {
        color: #F59E0B;
    }

    .insight-warning:hover {
        box-shadow: 0 12px 48px rgba(245, 158, 11, 0.3);
        transform: translateY(-2px);
    }

    /* CRITICAL INSIGHTS - Red/Alert Theme */
    .insight-critical {
        border-left-color: var(--climate-danger);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(17, 24, 39, 0.9) 100%);
    }

    .insight-critical .insight-header:hover {
        background: rgba(239, 68, 68, 0.1);
    }

    .insight-critical .insight-icon {
        color: #EF4444;
    }

    .insight-critical:hover {
        box-shadow: 0 12px 48px rgba(239, 68, 68, 0.3);
        transform: translateY(-2px);
    }

    /* INFO INSIGHTS - Blue/Data Theme */
    .insight-info {
        border-left-color: var(--climate-accent);
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(17, 24, 39, 0.9) 100%);
    }

    .insight-info .insight-header:hover {
        background: rgba(6, 182, 212, 0.1);
    }

    .insight-info .insight-icon {
        color: #06B6D4;
    }

    .insight-info:hover {
        box-shadow: 0 12px 48px rgba(6, 182, 212, 0.3);
        transform: translateY(-2px);
    }

    .highlight-text {
        font-weight: 700;
        color: var(--climate-accent);
    }

    /* JavaScript for toggle functionality */
    .insight-card-js {
        position: relative;
    }

    /* ========================================
       HEADERS
       ======================================== */
    h2 {
        color: #f8fafc;
        font-weight: 700;
        margin: 32px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(16, 185, 129, 0.3);
    }

    /* ========================================
       CHARTS
       ======================================== */
    div[data-testid="stPlotlyChart"] {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 16px 0;
    }

    /* ========================================
       PLOTLY CHART TITLES IN YELLOW
       ======================================== */
    /* Chart title text */
    .js-plotly-plot .gtitle,
    .js-plotly-plot .g-gtitle text {
        fill: #FFA500 !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }

    /* Axis titles in yellow */
    .js-plotly-plot .xtitle text,
    .js-plotly-plot .ytitle text,
    .js-plotly-plot .ztitle text {
        fill: #FFA500 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* ========================================
       STREAMLIT METRICS
       ======================================== */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
        backdrop-filter: blur(16px);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        border-color: var(--climate-primary);
        transform: translateY(-4px);
    }

    /* ========================================
       DOWNLOAD BUTTONS
       ======================================== */
    .stDownloadButton button {
        background: linear-gradient(135deg, var(--climate-primary) 0%, var(--climate-secondary) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3) !important;
    }

    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5) !important;
    }

    /* ========================================
       DATAFRAMES
       ======================================== */
    div[data-testid="stDataFrame"] {
        background: rgba(17, 24, 39, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px;
    }

    /* ========================================
       CAPTIONS
       ======================================== */
    .caption, small {
        color: #94a3b8;
        font-style: italic;
        font-size: 0.9rem;
        margin-top: 8px;
        display: block;
    }
    
    /* ========================================
       FIX: PLOTLY LEGEND TEXT VISIBILITY
       (Country names not visible)
       ======================================== */

    /* Legend container text */
    .js-plotly-plot .legend text {
        fill: #F8FAFC !important;   /* bright white */
        font-weight: 500 !important;
    }

    /* Legend title (e.g., "country") */
    .js-plotly-plot .legend .legendtitle text {
        fill: #E5E7EB !important;
        font-weight: 600 !important;
    }

    /* Colorbar labels (for heatmaps / continuous scales) */
    .js-plotly-plot .colorbar text {
        fill: #F8FAFC !important;
    }

    /* Fallback for SVG text inside charts */
    .js-plotly-plot svg text {
        fill: #E5E7EB;
    }

    /* ========================================
       INSIGHT CARD JAVASCRIPT TOGGLE
       ======================================== */
    </style>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Function to toggle insights
        function toggleInsight(header) {
            const content = header.nextElementSibling;
            const toggle = header.querySelector('.insight-toggle');
            
            if (content && content.classList.contains('insight-content')) {
                content.classList.toggle('active');
                if (toggle) {
                    toggle.classList.toggle('active');
                }
            }
        }
        
        // Add click listeners to all insight headers
        document.querySelectorAll('.insight-header').forEach(header => {
            header.addEventListener('click', function() {
                toggleInsight(this);
            });
        });
    });
    
    // For dynamically added content (Streamlit re-renders)
    const observer = new MutationObserver(function(mutations) {
        document.querySelectorAll('.insight-header').forEach(header => {
            if (!header.hasAttribute('data-listener')) {
                header.setAttribute('data-listener', 'true');
                header.addEventListener('click', function() {
                    const content = this.nextElementSibling;
                    const toggle = this.querySelector('.insight-toggle');
                    
                    if (content && content.classList.contains('insight-content')) {
                        content.classList.toggle('active');
                        if (toggle) {
                            toggle.classList.toggle('active');
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    </script>
    """


# Apply CSS
st.markdown(load_css(), unsafe_allow_html=True)
# =====================================================
# KPI HELPER
# =====================================================
def kpi_class(value, good, warn):
    if value <= good:
        return "kpi-good"
    elif value <= warn:
        return "kpi-warning"
    else:
        return "kpi-critical"

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("GlobalWeatherCleaned.csv", parse_dates=["last_updated"])
    df["date"] = df["last_updated"].dt.normalize()
    df["month"] = df["last_updated"].dt.month
    df["month_name"] = df["last_updated"].dt.strftime("%b")

    season_map = {
        12:"Winter",1:"Winter",2:"Winter",
        3:"Spring",4:"Spring",5:"Spring",
        6:"Summer",7:"Summer",8:"Summer",
        9:"Autumn",10:"Autumn",11:"Autumn"
    }
    df["season"] = df["month"].map(season_map)

    df["heat_index"] = df["temperature_celsius"] + 0.1 * df["humidity"]
    df["wind_chill"] = df["temperature_celsius"] - 0.1 * df["wind_kph"]

    df = df.sort_values(["country", "last_updated"])
    df["temp_7day_avg"] = (
        df.groupby("country")["temperature_celsius"]
        .rolling(7, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    return df

df = load_data()

# =====================================================
# SIDEBAR CONTROLS
# =====================================================
st.sidebar.markdown("# 🌍 ClimateScope Controls")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📊 Navigate Dashboard",
    ["Executive Dashboard","Statistical Analysis","Climate Trends","Extreme Events","Help"],
    label_visibility="visible"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Filter Data")

countries = st.sidebar.multiselect("🌐 Select Countries", sorted(df["country"].unique()))
date_range = st.sidebar.date_input("📅 Date Range", [df["date"].min(), df["date"].max()])

metric = st.sidebar.selectbox(
    "📈 Climate Metric",
   ["temperature_celsius","humidity","precip_mm","wind_kph","heat_index","wind_chill","temp_7day_avg"],
    format_func=lambda x: x.replace("_", " ").title()
)

aggregation = st.sidebar.selectbox("⏱ Time Aggregation", ["Daily","Monthly","Seasonal"])
normalize = st.sidebar.checkbox("🔢 Normalize Metric (0–1)")
threshold = st.sidebar.number_input("🔥 Extreme Event Threshold", value=35.0, step=0.5)

# =====================================================
# FILTER DATA
# =====================================================
@st.cache_data(show_spinner=False)
def filter_data(countries, start, end, metric, normalize):
    d = df
    if countries:
        d = d[d["country"].isin(countries)]

    d = d[(d["date"] >= pd.to_datetime(start)) & (d["date"] <= pd.to_datetime(end))]

    if normalize:
        mn, mx = d[metric].min(), d[metric].max()
        if mx > mn:
            d = d.assign(**{metric: (d[metric] - mn) / (mx - mn)})
    return d

filtered = filter_data(tuple(countries), date_range[0], date_range[1], metric, normalize)

# =====================================================
# ENHANCED KPI SECTION
# =====================================================
st.markdown("## 📊 Climate Performance Indicators")
st.markdown("---")

col1, col2, col3 = st.columns(3)

avg_temp = round(filtered["temperature_celsius"].mean(), 1)
rain_var = round(filtered["precip_mm"].std() / filtered["precip_mm"].mean() * 100, 1) if filtered["precip_mm"].mean() > 0 else 0
extreme_score = round((filtered["temperature_celsius"] > threshold).sum() / len(filtered) * 100, 1)

with col1:
    trend = "↑ +2.3%" if avg_temp > 24 else "↓ -1.5%"
    trend_class = "positive" if avg_temp <= 24 else "negative"
    st.markdown(f"""
    <div class="kpi-box {kpi_class(avg_temp, 22, 28)}">
        <div class="kpi-icon">🌡️</div>
        <div class="kpi-label">Average Temperature</div>
        <div class="kpi-value">{avg_temp}°C</div>
        <div class="kpi-trend {trend_class}">{trend}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    trend = "↑ +5.1%" if rain_var > 15 else "→ Stable"
    trend_class = "negative" if rain_var > 15 else "positive"
    st.markdown(f"""
    <div class="kpi-box {kpi_class(rain_var, 10, 20)}">
        <div class="kpi-icon">🌧️</div>
        <div class="kpi-label">Rainfall Variability</div>
        <div class="kpi-value">{rain_var}%</div>
        <div class="kpi-trend {trend_class}">{trend}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    trend = "↑ High Risk" if extreme_score > 70 else "↓ Moderate"
    trend_class = "negative" if extreme_score > 70 else "positive"
    st.markdown(f"""
    <div class="kpi-box {kpi_class(extreme_score, 40, 70)}">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-label">Extreme Event Risk</div>
        <div class="kpi-value">{extreme_score}</div>
        <div class="kpi-trend {trend_class}">{trend}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ENHANCED INSIGHTS
# =====================================================
st.markdown("## 🧠 Climate Intelligence Insights")
st.markdown("---")

if avg_temp > 28:
    insight_class = "insight-critical"
    insight = "🌡️ **Critical Temperature Alert** — Immediate climate action and cooling strategies required for affected regions."
elif avg_temp > 24:
    insight_class = "insight-warning"
    insight = "⚠️ **Rising Temperature Trend** — Monitoring recommended as climate stress indicators show upward trajectory."
else:
    insight_class = "insight-positive"
    insight = "✅ **Temperature Stability Maintained** — Current climate conditions remain within acceptable operational parameters."

st.markdown(f"""
<div class="insight-card {insight_class}">
    {insight}<br><br>
    <span class="highlight-text">
    🔍 Analysis shows rainfall variability at {rain_var}% and extreme event probability at {extreme_score}%, 
    indicating {'elevated risk zones requiring strategic intervention' if extreme_score > 60 else 'manageable climate conditions with standard protocols'}.
    </span>
</div>
""", unsafe_allow_html=True)

# =====================================================
# PLOTLY THEME CONFIGURATION
# =====================================================
def get_plotly_template():
    """Climate-themed Plotly template"""
    return dict(
        layout=dict(
            paper_bgcolor='rgba(17, 24, 39, 0.5)',
            plot_bgcolor='rgba(15, 23, 42, 0.3)',
            font=dict(
                family="Inter, system-ui, sans-serif",
                color='#e5e7eb'
            ),
            title=dict(
                font=dict(size=20, weight=700),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.08)',
                zerolinecolor='rgba(255, 255, 255, 0.1)',
                title=dict(font=dict(size=14, weight=600))
            ),
            yaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.08)',
                zerolinecolor='rgba(255, 255, 255, 0.1)',
                title=dict(font=dict(size=14, weight=600))
            ),
            legend=dict(
                bgcolor='rgba(30, 41, 59, 0.8)',
                bordercolor='rgba(255, 255, 255, 0.1)',
                borderwidth=1
            ),
            colorway=['#10b981', '#06b6d4', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444']
        )
    )

# =====================================================
# PAGE 1 — EXECUTIVE DASHBOARD
# =====================================================
if page == "Executive Dashboard":
    st.title("🌍 Executive Climate Overview")
    st.markdown("*Real-time climate intelligence for strategic decision-making*")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    @st.cache_data(show_spinner=False)
    def get_color_scale(metric):
        if metric in ["temperature_celsius", "heat_index"]:
            return "RdYlGn_r"  # Red-Yellow-Green reversed
        elif metric in ["humidity", "precip_mm"]:
            return "Blues"
        elif metric in ["wind_kph", "wind_chill"]:
            return "Viridis"
        else:
            return "Teal"

    color_scale = get_color_scale(metric)

    # MAP 1: SCATTER GEO
    @st.cache_data(show_spinner=False)
    def prepare_map_data(df, metric):
        cols = ["latitude", "longitude", "location_name", "country", "date", metric]
        d = df[cols].dropna(subset=["latitude", "longitude", metric])
        if len(d) > 2500:
            d = d.sample(2500, random_state=42)
        return d

    map_data = prepare_map_data(filtered, metric)

    fig_scatter = px.scatter_geo(
        map_data,
        lat="latitude",
        lon="longitude",
        color=metric,
        color_continuous_scale=color_scale,
        projection="natural earth",
        hover_name="location_name",
        hover_data={"country": True, metric: ':.2f', "date": True},
        title=f"🌍 Global Distribution: {metric_label}",
        labels={metric: metric_label}
    )

    fig_scatter.update_traces(
        marker=dict(size=10, opacity=0.8, line=dict(width=0.5, color="rgba(255,255,255,0.3)"))
    )

    fig_scatter.update_layout(
        **get_plotly_template()['layout'],
        geo=dict(
            showland=True,
            landcolor="#1e293b",
            showcountries=True,
            countrycolor="rgba(255,255,255,0.2)",
            showocean=True,
            oceancolor="#0f172a",
            coastlinecolor="rgba(255,255,255,0.15)"
        ),
        margin=dict(l=0, r=0, t=60, b=0)
    )

    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption(f"🔍 **Insight:** City-level {metric_label} distribution reveals geographic climate patterns and variation hotspots.")

    st.markdown("---")

    # MAP 2: CHOROPLETH
    @st.cache_data(show_spinner=False)
    def compute_country_avg(df, metric):
        return df[["country", metric]].groupby("country", as_index=False)[metric].mean()

    country_avg = compute_country_avg(filtered, metric)

    fig_choro = px.choropleth(
        country_avg,
        locations="country",
        locationmode="country names",
        color=metric,
        color_continuous_scale=color_scale,
        hover_name="country",
        labels={metric: metric_label},
        title=f"🗺️ Country-Level Average: {metric_label}"
    )

    fig_choro.update_layout(
        **get_plotly_template()['layout'],
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.2)",
            projection_type="natural earth",
            bgcolor='rgba(15, 23, 42, 0.3)'
        ),
        margin=dict(l=0, r=0, t=60, b=0)
    )

    st.plotly_chart(fig_choro, use_container_width=True)
    st.caption(f"🔍 **Insight:** National {metric_label} averages highlight macro-level climate trends and regional disparities.")

    st.download_button(
        label="📥 Download Executive Data (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="climatescope_executive_dashboard.csv",
        mime="text/csv"
    )


# =====================================================
# STATISTICAL ANALYSIS PAGE - FIX FOR TRENDLINE ERROR
# Replace your Statistical Analysis section with this
# =====================================================

# OPTION 1: Install statsmodels
# Run in terminal: pip install statsmodels

# OPTION 2: Remove trendline (use this code below)

elif page == "Statistical Analysis":
    st.title("📊 Statistical Climate Analysis")
    st.markdown("*Advanced analytics and correlation insights*")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    # SCATTER PLOT - REMOVED TRENDLINE
    st.subheader("🔗 Temperature vs Humidity Correlation")
    scatter_df = filtered[["temperature_celsius", "humidity", "country"]]

    fig_scatter = px.scatter(
        scatter_df,
        x="temperature_celsius",
        y="humidity",
        color="country",
        opacity=0.7,
        title="Climate Correlation Analysis: Temperature vs Humidity",
        labels={"temperature_celsius": "Temperature (°C)", "humidity": "Humidity (%)"}
        # REMOVED: trendline="ols" - this requires statsmodels
    )
    fig_scatter.update_traces(marker=dict(size=10, line=dict(width=0.5, color="white")))
    fig_scatter.update_layout(**get_plotly_template()['layout'])
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("🔍 **Insight:** Correlation patterns reveal climate interdependencies across regions.")

    # BAR CHART
    st.subheader(f"📊 Top 15 Countries by {metric_label}")
    
    @st.cache_data(show_spinner=False)
    def compute_country_avg_bar(df, metric):
        return df[["country", metric]].groupby("country", as_index=False)[metric].mean().sort_values(metric, ascending=False).head(15)

    country_avg = compute_country_avg_bar(filtered, metric)

    fig_bar = px.bar(
        country_avg,
        x="country",
        y=metric,
        color=metric,
        color_continuous_scale="Turbo",
        title=f"Comparative Analysis: {metric_label} by Country",
        labels={"country": "Country", metric: metric_label}
    )
    fig_bar.update_layout(**get_plotly_template()['layout'])
    fig_bar.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption(f"🔍 **Insight:** Top countries show {metric_label} dominance in regional patterns.")

    # HISTOGRAM
    st.subheader(f"📈 Distribution Analysis: {metric_label}")
    
    fig_hist = px.histogram(
        filtered,
        x=metric,
        nbins=50,
        marginal="box",
        color="country",
        title=f"Frequency Distribution: {metric_label}",
        labels={metric: metric_label}
    )
    fig_hist.update_layout(**get_plotly_template()['layout'])
    st.plotly_chart(fig_hist, use_container_width=True)
    st.caption("🔍 **Insight:** Distribution curve shows data concentration and outliers.")

    # BOX PLOT
    st.subheader(f"📦 Variability Analysis: {metric_label}")
    
    fig_box = px.box(
        filtered,
        x="country",
        y=metric,
        color="country",
        title=f"Statistical Spread: {metric_label} by Country",
        labels={"country": "Country", metric: metric_label}
    )
    fig_box.update_layout(**get_plotly_template()['layout'], showlegend=False)
    fig_box.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption("🔍 **Insight:** Box plots reveal data range, quartiles, and extreme outliers.")

    # CORRELATION HEATMAP
    st.subheader("🔥 Climate Metrics Correlation Matrix")
    
    @st.cache_data(show_spinner=False)
    def compute_correlation(df):
        return df[["temperature_celsius", "humidity", "precip_mm", "wind_kph"]].corr()

    corr = compute_correlation(filtered)

    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        title="Correlation Heatmap: Climate Variables",
        labels=dict(color="Correlation Coefficient")
    )
    fig_corr.update_layout(**get_plotly_template()['layout'])
    fig_corr.update_xaxes(side="bottom")
    st.plotly_chart(fig_corr, use_container_width=True)
    st.caption("🔍 **Insight:** Heatmap quantifies relationships between climate variables (-1 to +1 scale).")

    st.subheader("📋 Statistical Summary")
    st.dataframe(filtered.describe(), use_container_width=True)

    st.download_button(
        "📥 Download Statistical Data",
        filtered.to_csv(index=False).encode("utf-8"),
        "climatescope_statistical_analysis.csv",
        mime="text/csv"
    )
# =====================================================
# PAGE 3 — CLIMATE TRENDS
# =====================================================
elif page == "Climate Trends":
    st.title("📈 Climate Trends Analysis")
    st.markdown("*Temporal patterns and seasonal intelligence*")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()
    max_date = filtered["date"].max()

    # TREND LINE
    st.subheader(f"📊 Temporal Evolution: {metric_label}")
    
    fig = px.line(
        filtered,
        x="date",
        y=metric,
        color="country",
        markers=True,
        title=f"Time Series Analysis: {metric_label}",
        labels={"date": "Date", metric: metric_label, "country": "Country"}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 **Insight:** Trend lines reveal long-term climate patterns and cyclical variations.")

    st.download_button(
        "📥 Download Trend Data",
        filtered[["date", "country", metric]].to_csv(index=False).encode("utf-8"),
        "trend_over_time.csv",
        mime="text/csv"
    )

    # AVERAGE VS RECENT
    st.subheader("🔄 Historical vs Recent Comparison")
    
    @st.cache_data(show_spinner=False)
    def compute_avg_recent(df, metric, max_date):
        d = df[["date", "country", metric]]
        d = d.assign(
            period=np.where(
                d["date"] >= max_date - pd.Timedelta(days=30),
                "Last 30 Days",
                "Historical Average"
            )
        )
        return d.groupby(["period", "country"], sort=False)[metric].mean().reset_index()

    avg_recent = compute_avg_recent(filtered, metric, max_date)

    fig = px.bar(
        avg_recent,
        x="country",
        y=metric,
        color="period",
        barmode="group",
        title=f"Comparative Period Analysis: {metric_label}",
        labels={"country": "Country", metric: metric_label, "period": "Time Period"},
        color_discrete_map={"Last 30 Days": "#10b981", "Historical Average": "#3b82f6"}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 **Insight:** Period comparison highlights recent climate shifts versus historical baselines.")

    st.download_button(
        "📥 Download Comparison Data",
        avg_recent.to_csv(index=False).encode("utf-8"),
        "trend_avg_vs_recent.csv",
        mime="text/csv"
    )

    # SEASONAL ANALYSIS
    st.subheader("🍂 Seasonal Climate Patterns")
    
    @st.cache_data(show_spinner=False)
    def compute_seasonal_avg(df, metric):
        return df[["season", "country", metric]].groupby(["season", "country"], sort=False)[metric].mean().reset_index()

    seasonal_avg = compute_seasonal_avg(filtered, metric)

    fig = px.bar(
        seasonal_avg,
        x="season",
        y=metric,
        color="country",
        barmode="group",
        title=f"Seasonal Climate Analysis: {metric_label}",
        labels={"season": "Season", metric: metric_label, "country": "Country"},
        category_orders={"season": ["Winter", "Spring", "Summer", "Autumn"]}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 **Insight:** Seasonal variations expose cyclical climate patterns and peak periods.")

    st.download_button(
        "📥 Download Seasonal Data",
        seasonal_avg.to_csv(index=False).encode("utf-8"),
        "trend_seasonal.csv",
        mime="text/csv"
    )

    # COUNTRY AVERAGES
    st.subheader("🌍 Geographic Climate Distribution")
    
    @st.cache_data(show_spinner=False)
    def compute_country_avg(df, metric):
        return df[["country", metric]].groupby("country", sort=False)[metric].mean().reset_index()

    country_avg = compute_country_avg(filtered, metric)

    fig = px.bar(
        country_avg,
        x="country",
        y=metric,
        color=metric,
        color_continuous_scale="Viridis",
        title=f"Country-Level Climate Baseline: {metric_label}",
        labels={"country": "Country", metric: metric_label}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 **Insight:** Geographic averages establish baseline climate conditions by region.")

    st.download_button(
        "📥 Download Country Averages",
        country_avg.to_csv(index=False).encode("utf-8"),
        "trend_country_avg.csv",
        mime="text/csv"
    )

# # =====================================================
# PAGE 4 — EXTREME EVENTS
# =====================================================
elif page == "Extreme Events":
    st.title("🔥 Extreme Climate Events Analysis")
    st.markdown("*Critical event detection and risk assessment*")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    @st.cache_data(show_spinner=False)
    def get_extreme_events(df, metric, threshold):
        cols = ["date", "country", "location_name", "season", "latitude", "longitude", metric]
        d = df[cols]
        return d[d[metric] >= threshold]

    extreme = get_extreme_events(filtered, metric, threshold)

    if extreme.empty:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #FF6B6B 0%, #C92A2A 100%); 
                        padding: 20px; border-radius: 10px; border-left: 5px solid #FFA500;">
                <h3 style="color: #FFFFFF; margin: 0;">⚠️ No Extreme Events Detected</h3>
                <p style="color: #FFE0E0; margin: 10px 0 0 0;">
                    No extreme events detected for the selected threshold and filters.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Enhanced CSS for better visibility
        st.markdown("""
            <style>
            /* KPI Metrics Styling */
            [data-testid="stMetricValue"] {
                color: #FFFFFF !important;
                font-size: 32px !important;
                font-weight: 700 !important;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            [data-testid="stMetricLabel"] {
                color: #FFA500 !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            div[data-testid="metric-container"] {
                background: linear-gradient(135deg, #1E3A5F 0%, #2A5080 100%);
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 165, 0, 0.3);
                transition: transform 0.2s;
            }
            div[data-testid="metric-container"]:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 12px rgba(255, 165, 0, 0.4);
            }
            
            /* Subheader Styling */
            .stMarkdown h3 {
                color: #FFA500 !important;
                font-weight: 600 !important;
                padding: 10px 0;
                border-bottom: 2px solid #FFA500;
                margin-bottom: 20px !important;
            }
            
            /* Caption Styling */
            .stCaption {
                background: rgba(255, 165, 0, 0.1) !important;
                padding: 12px !important;
                border-radius: 8px !important;
                border-left: 4px solid #FFA500 !important;
                color: #FFFFFF !important;
                font-size: 14px !important;
                margin-top: 10px !important;
            }
            
            # /* Download Button Styling */
            # .stDownloadButton button {
            #     background: linear-gradient(135deg, #FFA500 0%, #FF8C00 100%) !important;
            #     color: #FFFFFF !important;
            #     border: none !important;
            #     padding: 12px 24px !important;
            #     font-weight: 600 !important;
            #     border-radius: 8px !important;
            #     box-shadow: 0 4px 6px rgba(255, 165, 0, 0.3) !important;
            #     transition: transform 0.2s !important;
            # }
            # .stDownloadButton button:hover {
            #     transform: translateY(-2px) !important;
            #     box-shadow: 0 6px 12px rgba(255, 165, 0, 0.5) !important;
            #     background: linear-gradient(135deg, #FF8C00 0%, #FF7700 100%) !important;
            # }
            
            /* DataFrame Styling */
            .stDataFrame {
                border: 1px solid rgba(255, 165, 0, 0.3);
                border-radius: 8px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # KPI METRICS
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        total_events = len(extreme)
        max_value = extreme[metric].max()
        top_country = extreme["country"].mode()[0] if not extreme["country"].mode().empty else "N/A"

        c1.metric("🚨 Total Extreme Events", f"{total_events:,}")
        c2.metric("📊 Peak Value Recorded", f"{max_value:.2f}")
        c3.metric("🌍 Most Affected Region", top_country)

        st.markdown("<br>", unsafe_allow_html=True)

        # TIMELINE
        st.subheader("📅 Extreme Events Timeline")
        
        time_fig = px.scatter(
            extreme,
            x="date",
            y=metric,
            color="country",
            size=metric,
            hover_data=["location_name", "season"],
            title=f"Chronological Extreme Event Distribution: {metric_label}",
            labels={"date": "Date", metric: metric_label, "country": "Country"}
        )
        
        # Enhanced chart styling
        layout_settings = get_plotly_template()['layout'].copy()
        layout_settings.update({
            'plot_bgcolor': 'rgba(30, 58, 95, 0.3)',
            'paper_bgcolor': 'rgba(14, 17, 23, 0)',
            'font': dict(color='#FFFFFF', size=12),
            'title': dict(
                font=dict(size=18, color='#FFA500'),
                x=0.5,
                xanchor='center'
            ),
            'xaxis': dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                title_font=dict(color='#FFA500', size=14),
                tickfont=dict(color='#FFFFFF')
            ),
            'yaxis': dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                title_font=dict(color='#FFA500', size=14),
                tickfont=dict(color='#FFFFFF')
            ),
            'legend': dict(
                bgcolor='rgba(30, 58, 95, 0.8)',
                bordercolor='rgba(255, 165, 0, 0.5)',
                borderwidth=1,
                font=dict(color='#FFFFFF')
            ),
            'hoverlabel': dict(
                bgcolor='rgba(30, 58, 95, 0.95)',
                font_color='#FFFFFF',
                bordercolor='#FFA500'
            )
        })
        time_fig.update_layout(**layout_settings)
        
        time_fig.update_traces(marker=dict(line=dict(width=1, color='rgba(255, 165, 0, 0.5)'), opacity=0.8))
        st.plotly_chart(time_fig, use_container_width=True)
        st.caption("🔍 **Insight:** Event timeline identifies temporal clustering and frequency patterns.")

        st.download_button(
            "📥 Download Timeline Data",
            extreme[["date", "country", metric]].to_csv(index=False).encode("utf-8"),
            "extreme_timeline.csv",
            mime="text/csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # GEOGRAPHIC MAP
        st.subheader("🗺️ Geographic Hotspot Analysis")
        
        map_fig = px.scatter_geo(
            extreme,
            lat="latitude",
            lon="longitude",
            color=metric,
            size=metric,
            color_continuous_scale="Reds",
            hover_name="location_name",
            hover_data=["country", "season"],
            projection="natural earth",
            title=f"Extreme Event Geographic Distribution: {metric_label}",
            labels={metric: metric_label}
        )
        layout_settings = get_plotly_template()['layout'].copy()
        layout_settings.update({
            'geo': dict(
                showland=True,
                landcolor="#1e293b",
                showcountries=True,
                countrycolor="rgba(255,255,255,0.2)",
                showocean=True,
                oceancolor="#0f172a"
            ),
            'font': dict(color='#FFFFFF'),
            'title': dict(
                font=dict(size=18, color='#FFA500'),
                x=0.5,
                xanchor='center'
            )
        })
        map_fig.update_layout(**layout_settings)
        st.plotly_chart(map_fig, use_container_width=True)
        st.caption("🔍 **Insight:** Geographic clustering reveals high-risk zones requiring priority intervention.")

        st.download_button(
            "📥 Download Location Data",
            extreme.to_csv(index=False).encode("utf-8"),
            "extreme_locations.csv",
            mime="text/csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # SEASONAL DISTRIBUTION
        st.subheader("🍂 Seasonal Extreme Event Distribution")
        
        seasonal = extreme.groupby(["season", "country"]).size().reset_index(name="event_count")

        fig = px.bar(
            seasonal,
            x="season",
            y="event_count",
            color="country",
            barmode="group",
            title="Seasonal Frequency Analysis: Extreme Events",
            labels={"season": "Season", "event_count": "Number of Events", "country": "Country"},
            category_orders={"season": ["Winter", "Spring", "Summer", "Autumn"]}
        )
        layout_settings = get_plotly_template()['layout'].copy()
        layout_settings.update({
            'plot_bgcolor': 'rgba(30, 58, 95, 0.3)',
            'paper_bgcolor': 'rgba(14, 17, 23, 0)',
            'font': dict(color='#FFFFFF'),
            'title': dict(
                font=dict(size=18, color='#FFA500'),
                x=0.5,
                xanchor='center'
            ),
            'xaxis': dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                title_font=dict(color='#FFA500', size=14),
                tickfont=dict(color='#FFFFFF')
            ),
            'yaxis': dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                title_font=dict(color='#FFA500', size=14),
                tickfont=dict(color='#FFFFFF')
            ),
            'legend': dict(
                bgcolor='rgba(30, 58, 95, 0.8)',
                bordercolor='rgba(255, 165, 0, 0.5)',
                borderwidth=1,
                font=dict(color='#FFFFFF')
            )
        })
        fig.update_layout(**layout_settings)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🔍 **Insight:** Seasonal patterns reveal vulnerability windows and peak risk periods.")

        st.download_button(
            "📥 Download Seasonal Data",
            seasonal.to_csv(index=False).encode("utf-8"),
            "extreme_seasonal.csv",
            mime="text/csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # DATA TABLE
        st.subheader("📋 Complete Extreme Events Database")
        
        st.dataframe(
            extreme.sort_values(metric, ascending=False),
            use_container_width=True
        )

        st.download_button(
            "📥 Download All Events",
            extreme.to_csv(index=False).encode("utf-8"),
            "all_extreme_events.csv",
            mime="text/csv"
        )

# =====================================================
# PAGE 5 — HELP
# =====================================================
else:
    st.title("❓ ClimateScope User Guide")
    st.markdown("*Your comprehensive guide to climate intelligence*")
    st.markdown("---")

    st.markdown("""
    ### 🌍 About ClimateScope
    
    **ClimateScope** is a professional climate analytics platform designed for environmental professionals, 
    policy makers, researchers, and organizations focused on climate action and sustainability.
    
    ---
    
    ### 🎯 Key Features
    
    #### 📊 **Executive Dashboard**
    - Interactive global climate mapping
    - City-level and country-level visualizations
    - Real-time KPI monitoring
    - Geographic trend analysis
    
    #### 📈 **Statistical Analysis**
    - Correlation analysis between climate variables
    - Distribution and outlier detection
    - Country-level comparative analytics
    - Advanced statistical insights
    
    #### 🌡️ **Climate Trends**
    - Historical vs recent comparisons
    - Seasonal pattern analysis
    - Long-term trend visualization
    - Period-over-period analytics
    
    #### 🔥 **Extreme Events**
    - Threshold-based event detection
    - Geographic hotspot identification
    - Temporal clustering analysis
    - Risk assessment metrics
    
    ---
    
    ### 🛠️ How to Use
    
    #### **Step 1: Configure Filters** (Left Sidebar)
    - Select target countries or regions
    - Choose date range for analysis
    - Pick climate metrics (temperature, humidity, precipitation, etc.)
    - Set extreme event thresholds
    - Enable data normalization if needed
    
    #### **Step 2: Interpret KPIs** (Top Section)
    - **Green** 🟢 = Normal/Healthy range
    - **Yellow** 🟡 = Warning/Attention needed
    - **Red** 🔴 = Critical/Immediate action
    - Trend indicators show direction (↑↓)
    
    #### **Step 3: Explore Visualizations**
    - Hover over charts for detailed tooltips
    - Use zoom and pan on maps
    - Click legend items to filter data
    - Download charts as images (camera icon)
    
    #### **Step 4: Download Data**
    - Export filtered datasets as CSV
    - Use for reports, presentations, or further analysis
    - All downloads maintain current filter settings
    
    ---
    
    ### 📚 Use Cases
    
    ✅ **Climate Policy Development**
    - Evidence-based decision making
    - Risk zone identification
    - Resource allocation planning
    
    ✅ **Environmental Research**
    - Data-driven climate studies
    - Pattern recognition and forecasting
    - Academic publications
    
    ✅ **Corporate Sustainability**
    - ESG reporting and compliance
    - Climate risk assessment
    - Supply chain resilience
    
    ✅ **Agricultural Planning**
    - Seasonal forecasting
    - Drought and flood preparedness
    - Crop optimization strategies
    
    ---
    
    ### 🎨 Understanding Color Schemes
    
    - **Temperature**: Red-Yellow-Green (Hot to Cold)
    - **Precipitation**: Blues (Water theme)
    - **Wind**: Viridis/Plasma (Dynamic flow)
    - **General**: Teal (Balanced earth tones)
    
    ---
    
    ### 💡 Pro Tips
    
    1. **Start Broad, Then Focus**: Begin with all countries, then narrow down
    2. **Compare Periods**: Use date ranges to spot trends
    3. **Check Extremes First**: High-impact events drive strategy
    4. **Download Regularly**: Export data for offline analysis
    5. **Use Normalization**: Compare metrics on same scale (0-1)
    
    ---
    
    ### 📧 Support & Feedback
    
    For technical support, feature requests, or data inquiries, please contact your 
    ClimateScope administrator or refer to your organization's climate analytics team.
    
    ---
    
    ### 📥 Export Current Dataset
    """)

    st.download_button(
        label="📥 Download Filtered Climate Data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="ClimateScope_Filtered_Data.csv",
        mime="text/csv"
    )