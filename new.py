import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="ClimateScope Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# ENHANCED CSS (Your existing CSS)
# =====================================================
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

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    section[data-testid="stSidebar"] label {
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

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

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(16, 185, 129, 0.15) !important;
        border-color: #10b981 !important;
        color: #10b981 !important;
        transform: translateX(4px) !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.3) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border-color: #10b981 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4) !important;
        font-weight: 700 !important;
    }

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

    h2 {
        color: #f8fafc;
        font-weight: 700;
        margin: 32px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(16, 185, 129, 0.3);
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 16px 0;
    }

    .js-plotly-plot .gtitle,
    .js-plotly-plot .g-gtitle text {
        fill: #FFA500 !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }

    .js-plotly-plot .xtitle text,
    .js-plotly-plot .ytitle text,
    .js-plotly-plot .ztitle text {
        fill: #FFA500 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    .js-plotly-plot .legend text {
        fill: #F8FAFC !important;
        font-weight: 500 !important;
    }

    /* Journey Plan Specific Styles */
    .journey-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        border: 2px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .journey-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(16, 185, 129, 0.4);
        border-color: var(--climate-primary);
    }

    .journey-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #10b981;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .journey-score {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .activity-chip {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .warning-chip {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.3);
    }

    .packing-list {
        background: rgba(6, 182, 212, 0.08);
        border-left: 4px solid var(--climate-accent);
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
    }

    .packing-item {
        padding: 8px 0;
        color: #cbd5e1;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .season-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 4px;
    }

    .season-winter { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
    .season-spring { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .season-summer { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
    .season-autumn { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    </style>
    """

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
    ["Executive Dashboard","Statistical Analysis","Climate Trends","Extreme Events","Journey Planner 🧳","Help"],
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

if len(date_range) == 2:
    filtered = filter_data(
        tuple(countries), 
        date_range[0], 
        date_range[1], 
        metric, 
        normalize
    )
else:
    st.warning("Please select both start and end dates")
    filtered = df

# =====================================================
# PLOTLY THEME
# =====================================================
def get_plotly_template():
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
# JOURNEY PLANNER FUNCTIONS
# =====================================================
def calculate_travel_score(country_data):
    """Calculate a travel suitability score based on climate data"""
    temp_avg = country_data['temperature_celsius'].mean()
    temp_std = country_data['temperature_celsius'].std()
    humidity_avg = country_data['humidity'].mean()
    precip_avg = country_data['precip_mm'].mean()
    wind_avg = country_data['wind_kph'].mean()
    
    # Ideal conditions: 20-25°C, low humidity, low precipitation
    temp_score = 100 - abs(temp_avg - 22.5) * 4
    temp_score = max(0, min(100, temp_score))
    
    stability_score = 100 - (temp_std * 10)
    stability_score = max(0, min(100, stability_score))
    
    humidity_score = 100 - (abs(humidity_avg - 50) * 1.5)
    humidity_score = max(0, min(100, humidity_score))
    
    precip_score = max(0, 100 - (precip_avg * 10))
    
    wind_score = 100 - (wind_avg * 2)
    wind_score = max(0, min(100, wind_score))
    
    total_score = (temp_score * 0.35 + stability_score * 0.15 + 
                   humidity_score * 0.25 + precip_score * 0.15 + wind_score * 0.10)
    
    return round(total_score, 1)

def get_season_recommendations(country_data):
    """Get recommendations by season"""
    season_data = country_data.groupby('season').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'precip_mm': 'mean',
        'wind_kph': 'mean'
    }).round(1)
    
    recommendations = {}
    for season in season_data.index:
        temp = season_data.loc[season, 'temperature_celsius']
        humidity = season_data.loc[season, 'humidity']
        precip = season_data.loc[season, 'precip_mm']
        
        if 18 <= temp <= 28 and humidity < 70 and precip < 5:
            recommendations[season] = "Ideal"
        elif 15 <= temp <= 32 and humidity < 80:
            recommendations[season] = "Good"
        elif temp < 10 or temp > 35 or humidity > 85:
            recommendations[season] = "Challenging"
        else:
            recommendations[season] = "Moderate"
    
    return season_data, recommendations

def get_packing_suggestions(country_data):
    """Generate packing list based on climate"""
    temp_avg = country_data['temperature_celsius'].mean()
    precip_avg = country_data['precip_mm'].mean()
    wind_avg = country_data['wind_kph'].mean()
    
    items = []
    
    if temp_avg > 28:
        items.extend(["☀️ Sunscreen (SPF 50+)", "🧢 Wide-brimmed hat", "🕶️ Sunglasses", 
                     "👕 Light, breathable clothing", "💧 Reusable water bottle"])
    elif temp_avg > 22:
        items.extend(["🌤️ Light jacket for evenings", "👕 Comfortable walking shoes", 
                     "🕶️ Sunglasses", "💧 Water bottle"])
    elif temp_avg > 15:
        items.extend(["🧥 Medium-weight jacket", "🧣 Light scarf", "👕 Layered clothing", 
                     "☂️ Compact umbrella"])
    else:
        items.extend(["🧥 Warm winter coat", "🧤 Gloves", "🧣 Scarf", "❄️ Thermal wear", 
                     "🥾 Insulated boots"])
    
    if precip_avg > 3:
        items.extend(["☔ Waterproof jacket", "🌂 Sturdy umbrella", "👢 Water-resistant footwear"])
    
    if wind_avg > 20:
        items.append("🧥 Windbreaker jacket")
    
    items.extend(["📱 Weather app", "🔌 Power adapter", "💊 Basic first aid kit"])
    
    return items

def get_activity_suggestions(country_data):
    """Suggest activities based on climate"""
    temp_avg = country_data['temperature_celsius'].mean()
    precip_avg = country_data['precip_mm'].mean()
    
    activities = []
    warnings = []
    
    if 20 <= temp_avg <= 30 and precip_avg < 3:
        activities.extend(["🏖️ Beach activities", "🚶 Hiking & trekking", "🚴 Cycling tours", 
                          "📸 Photography walks", "🍽️ Outdoor dining"])
    elif 15 <= temp_avg < 20:
        activities.extend(["🏛️ Museum visits", "🏰 Historical site tours", "☕ Café hopping", 
                          "🛍️ Shopping districts", "🎭 Cultural performances"])
    elif temp_avg < 15:
        activities.extend(["⛷️ Winter sports", "🏔️ Mountain activities", "🎿 Skiing", 
                          "☕ Cozy indoor experiences", "🏛️ Indoor attractions"])
    else:
        activities.extend(["🏊 Water parks", "🛶 Water sports", "🌳 Shaded park visits", 
                          "❄️ Air-conditioned museums", "🌙 Evening/night activities"])
    
    if temp_avg > 35:
        warnings.append("⚠️ Extreme heat - plan indoor activities during midday")
    if precip_avg > 5:
        warnings.append("⚠️ High rainfall - bring rain gear and plan flexible itinerary")
    if temp_avg < 5:
        warnings.append("⚠️ Very cold - ensure proper winter clothing")
    
    return activities, warnings

# =====================================================
# JOURNEY PLANNER PAGE (NEW)
# =====================================================
if page == "Journey Planner 🧳":
    st.title("✈️ ClimateScope Journey Planner")
    st.markdown("*AI-powered travel planning based on real climate intelligence*")
    st.markdown("---")
    
    # Destination Selection
    st.markdown("## 🎯 Select Your Destination")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        destination_country = st.selectbox(
            "🌍 Choose your destination country",
            sorted(df['country'].unique()),
            help="Select a country to get personalized climate-based travel recommendations"
        )
    
    with col2:
        travel_month = st.selectbox(
            "📅 Preferred Travel Month",
            ["Any", "January", "February", "March", "April", "May", "June", 
             "July", "August", "September", "October", "November", "December"]
        )
    
    # Filter data for selected country
    country_data = df[df['country'] == destination_country].copy()
    
    if travel_month != "Any":
        month_num = datetime.strptime(travel_month, "%B").month
        country_data = country_data[country_data['month'] == month_num]
    
    if len(country_data) == 0:
        st.warning(f"No climate data available for {destination_country} in {travel_month}")
    else:
        # Calculate travel score
        travel_score = calculate_travel_score(country_data)
        
        # Display Travel Score
        st.markdown("---")
        st.markdown("## 🌟 Climate Comfort Score")
        
        score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
        
        with score_col2:
            score_color = "#10b981" if travel_score >= 70 else "#f59e0b" if travel_score >= 50 else "#ef4444"
            score_label = "Excellent" if travel_score >= 70 else "Good" if travel_score >= 50 else "Challenging"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 40px 20px; 
                        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(17, 24, 39, 0.9) 100%);
                        border-radius: 20px; border: 3px solid {score_color}; 
                        box-shadow: 0 12px 48px rgba(16, 185, 129, 0.3);">
                <div style="font-size: 5rem; font-weight: 800; color: {score_color}; 
                           text-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
                    {travel_score}
                </div>
                <div style="font-size: 1.5rem; font-weight: 600; color: #cbd5e1; margin-top: 10px;">
                    {score_label} Conditions
                </div>
                <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 8px;">
                    Based on temperature, humidity, precipitation & wind analysis
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Climate Overview KPIs
        st.markdown("---")
        st.markdown("## 🌡️ Climate Overview")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        avg_temp = country_data['temperature_celsius'].mean()
        avg_humidity = country_data['humidity'].mean()
        avg_precip = country_data['precip_mm'].mean()
        avg_wind = country_data['wind_kph'].mean()
        
        with kpi1:
            st.markdown(f"""
            <div class="kpi-box kpi-good">
                <div class="kpi-icon">🌡️</div>
                <div class="kpi-label">Avg Temperature</div>
                <div class="kpi-value">{avg_temp:.1f}°C</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi2:
            st.markdown(f"""
            <div class="kpi-box kpi-warning">
                <div class="kpi-icon">💧</div>
                <div class="kpi-label">Humidity</div>
                <div class="kpi-value">{avg_humidity:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi3:
            st.markdown(f"""
            <div class="kpi-box kpi-good">
                <div class="kpi-icon">🌧️</div>
                <div class="kpi-label">Precipitation</div>
                <div class="kpi-value">{avg_precip:.1f}mm</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi4:
            st.markdown(f"""
            <div class="kpi-box kpi-warning">
                <div class="kpi-icon">💨</div>
                <div class="kpi-label">Wind Speed</div>
                <div class="kpi-value">{avg_wind:.1f}kph</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Seasonal Analysis
        st.markdown("---")
        st.markdown("## 🍂 Best Time to Visit")
        
        season_data, recommendations = get_season_recommendations(country_data)
        
        season_cols = st.columns(4)
        season_order = ["Winter", "Spring", "Summer", "Autumn"]
        season_icons = {"Winter": "❄️", "Spring": "🌸", "Summer": "☀️", "Autumn": "🍁"}
        
        for idx, season in enumerate(season_order):
            if season in season_data.index:
                with season_cols[idx]:
                    temp = season_data.loc[season, 'temperature_celsius']
                    rec = recommendations[season]
                    
                    rec_color = "#10b981" if rec == "Ideal" else "#3b82f6" if rec == "Good" else "#f59e0b" if rec == "Moderate" else "#ef4444"
                    
                    st.markdown(f"""
                    <div class="journey-card">
                        <div style="text-align: center;">
                            <div style="font-size: 2.5rem; margin-bottom: 8px;">{season_icons[season]}</div>
                            <div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc; margin-bottom: 8px;">{season}</div>
                            <div style="font-size: 1.8rem; font-weight: 700; color: {rec_color}; margin: 12px 0;">
                                {temp:.1f}°C
                            </div>
                            <span class="season-badge" style="background: rgba(16, 185, 129, 0.2); color: {rec_color};">
                                {rec}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Temperature Trend Chart
        st.markdown("---")
        st.markdown("## 📊 Temperature Trends")
        
        monthly_temp = country_data.groupby('month_name')['temperature_celsius'].agg(['mean', 'min', 'max']).reset_index()
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_temp['month_name'] = pd.Categorical(monthly_temp['month_name'], categories=month_order, ordered=True)
        monthly_temp = monthly_temp.sort_values('month_name')
        
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=monthly_temp['month_name'],
            y=monthly_temp['max'],
            name='High',
            line=dict(color='#ef4444', width=2),
            mode='lines+markers'
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=monthly_temp['month_name'],
            y=monthly_temp['mean'],
            name='Average',
            line=dict(color='#10b981', width=3),
            mode='lines+markers',
            marker=dict(size=8)
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=monthly_temp['month_name'],
            y=monthly_temp['min'],
            name='Low',
            line=dict(color='#3b82f6', width=2),
            mode='lines+markers'
        ))
        
        # fig_temp.update_layout(
        #     **get_plotly_template()['layout'],
        #     title=f"Annual Temperature Range - {destination_country}",
        #     xaxis_title="Month",
        #     yaxis_title="Temperature (°C)",
        #     hovermode='x unified'
        # )
        layout = get_plotly_template()['layout'].copy()
        layout.pop("title", None)  # remove title if it exists

        fig_temp.update_layout(
            **layout,
            title=f"Annual Temperature Range - {destination_country}",
            xaxis_title="Month",
            yaxis_title="Temperature (°C)",
            hovermode='x unified'
        )

        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Activities & Packing
        st.markdown("---")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("## 🎯 Recommended Activities")
            activities, warnings = get_activity_suggestions(country_data)
            
            st.markdown('<div class="journey-card">', unsafe_allow_html=True)
            for activity in activities:
                st.markdown(f'<span class="activity-chip">{activity}</span>', unsafe_allow_html=True)
            
            if warnings:
                st.markdown("<br><br><strong style='color: #f59e0b;'>⚠️ Important Considerations:</strong>", unsafe_allow_html=True)
                for warning in warnings:
                    st.markdown(f'<span class="activity-chip warning-chip">{warning}</span>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown("## 🎒 Packing Essentials")
            packing_items = get_packing_suggestions(country_data)
            
            st.markdown('<div class="packing-list">', unsafe_allow_html=True)
            for item in packing_items:
                st.markdown(f'<div class="packing-item">{item}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Location Map
        st.markdown("---")
        st.markdown("## 🗺️ Location Climate Hotspots")
        
        location_data = country_data.groupby('location_name').agg({
            'latitude': 'first',
            'longitude': 'first',
            'temperature_celsius': 'mean',
            'humidity': 'mean'
        }).reset_index()
        
        fig_map = px.scatter_geo(
            location_data,
            lat='latitude',
            lon='longitude',
            color='temperature_celsius',
            size='humidity',
            hover_name='location_name',
            hover_data={'temperature_celsius': ':.1f', 'humidity': ':.0f'},
            title=f"Climate Conditions Across {destination_country}",
            color_continuous_scale='RdYlGn_r',
            labels={'temperature_celsius': 'Avg Temp (°C)', 'humidity': 'Humidity (%)'}
        )
        
        fig_map.update_geos(
            showcountries=True,
            countrycolor="rgba(255, 255, 255, 0.3)",
            showcoastlines=True,
            coastlinecolor="rgba(255, 255, 255, 0.3)",
            projection_type="natural earth",
            bgcolor='rgba(15, 23, 42, 0.3)'
        )
        
        fig_map.update_layout(**get_plotly_template()['layout'])
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Travel Tips
        st.markdown("---")
        st.markdown("## 💡 Pro Travel Tips")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown("""
            <div class="journey-card">
                <div class="journey-header">🎫 Planning Advice</div>
                <div style="color: #cbd5e1; line-height: 1.8;">
                    ✅ Book flights 2-3 months in advance for best prices<br>
                    ✅ Check visa requirements early<br>
                    ✅ Get travel insurance with climate coverage<br>
                    ✅ Download offline maps and translation apps<br>
                    ✅ Notify your bank of international travel
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with tips_col2:
            st.markdown(f"""
            <div class="journey-card">
                <div class="journey-header">🏥 Health & Safety</div>
                <div style="color: #cbd5e1; line-height: 1.8;">
                    ✅ Check vaccination requirements<br>
                    ✅ Pack prescription medications with documentation<br>
                    ✅ Stay hydrated (especially if temp > {avg_temp:.0f}°C)<br>
                    ✅ Use sunscreen in high UV conditions<br>
                    ✅ Have emergency contacts saved offline
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Download Journey Plan
        st.markdown("---")
        st.markdown("## 📥 Export Your Journey Plan")
        
        journey_summary = pd.DataFrame({
            'Metric': ['Climate Score', 'Avg Temperature', 'Humidity', 'Precipitation', 'Wind Speed'],
            'Value': [f"{travel_score}/100", f"{avg_temp:.1f}°C", f"{avg_humidity:.0f}%", 
                     f"{avg_precip:.1f}mm", f"{avg_wind:.1f}kph"]
        })
        
        st.download_button(
            label="📥 Download Journey Plan (CSV)",
            data=journey_summary.to_csv(index=False).encode('utf-8'),
            file_name=f"journey_plan_{destination_country.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

# =====================================================
# [REST OF YOUR ORIGINAL CODE - Executive Dashboard, Statistical Analysis, etc.]
# =====================================================

elif page == "Executive Dashboard":
    st.title("🌍 Executive Climate Overview")
    st.markdown("*Real-time climate intelligence for strategic decision-making*")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    @st.cache_data(show_spinner=False)
    def get_color_scale(metric):
        if metric in ["temperature_celsius", "heat_index"]:
            return "RdYlGn_r"
        elif metric in ["humidity", "precip_mm"]:
            return "Blues"
        elif metric in ["wind_kph", "wind_chill"]:
            return "Viridis"
        else:
            return "Teal"

    color_scale = get_color_scale(metric)

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

    # KPI Section
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

    st.download_button(
        label="📥 Download Executive Data (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="climatescope_executive_dashboard.csv",
        mime="text/csv"
    )

elif page == "Help":
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
    
    #### ✈️ **Journey Planner** (NEW!)
    - AI-powered travel recommendations based on climate data
    - Seasonal analysis and best time to visit
    - Activity suggestions based on weather patterns
    - Climate-optimized packing lists
    - Location-specific climate insights
    
    #### 📈 **Statistical Analysis**
    - Correlation analysis between climate variables
    - Distribution and outlier detection
    - Country-level comparative analytics
    
    #### 🌡️ **Climate Trends**
    - Historical vs recent comparisons
    - Seasonal pattern analysis
    - Long-term trend visualization
    
    #### 🔥 **Extreme Events**
    - Threshold-based event detection
    - Geographic hotspot identification
    - Risk assessment metrics
    
    ---
    
    ### 🧳 Using the Journey Planner
    
    1. **Select Your Destination**: Choose from available countries
    2. **Pick Travel Month**: Specify when you plan to visit (or select "Any")
    3. **Review Climate Score**: See overall travel comfort rating (0-100)
    4. **Check Seasonal Recommendations**: Find the best time to visit
    5. **Get Activity Suggestions**: Discover what to do based on weather
    6. **Pack Smart**: Use the generated packing list
    7. **Export Your Plan**: Download a complete journey summary
    
    ---
    
    ### 💡 Pro Tips
    
    1. **Start Broad, Then Focus**: Begin with all countries, then narrow down
    2. **Compare Periods**: Use date ranges to spot trends
    3. **Use Journey Planner**: Optimize travel timing with climate data
    4. **Download Regularly**: Export data for offline analysis
    5. **Check Extremes First**: High-impact events drive strategy
    
    ---
    
    ### 📧 Support & Feedback
    
    For technical support or feature requests, please contact your ClimateScope administrator.
    """)

    st.download_button(
        label="📥 Download Filtered Climate Data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="ClimateScope_Filtered_Data.csv",
        mime="text/csv"
    )

# Add the remaining pages (Statistical Analysis, Climate Trends, Extreme Events) from your original code here
# I've kept Executive Dashboard and Help as examples - you should add the other pages back in