import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime



# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0b0f19, #0e1117);
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f19, #111827);
    border-right: 1px solid #1f2937;
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* KPI CARDS */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 16px;
    padding: 20px;
    color: white;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

/* KPI LABEL */
div[data-testid="metric-container"] label {
    font-size: 14px;
    opacity: 0.85;
}

/* KPI VALUE */
div[data-testid="metric-container"] div {
    font-size: 28px;
    font-weight: 700;
}

/* TABS */
button[data-baseweb="tab"] {
    background-color: #0f172a !important;
    color: #c7d2fe !important;
    border-radius: 10px 10px 0 0;
    margin-right: 4px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
}

/* HEADINGS */
h1, h2, h3 {
    color: #93c5fd;
    font-weight: 600;
}

/* DATAFRAME */
.stDataFrame {
    background-color: #020617 !important;
}

/* REMOVE WHITE BLOCKS */
div.block-container {
    padding-top: 1.5rem;
}

/* SLIDERS */
.stSlider > div {
    color: #a5b4fc;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Global Weather Data Analysis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/cleaned_weather.csv")
    
    
    
    

    # datetime safe
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    # -------------------------------
# Heat Index (Feels Like Temp)
# Formula valid for temp >= 27°C and humidity >= 40%
# -------------------------------
    def calculate_heat_index(temp_c, humidity):
        if pd.isna(temp_c) or pd.isna(humidity):
            return np.nan
        if temp_c < 27 or humidity < 40:
            return temp_c

        # Convert to Fahrenheit
        T = (temp_c * 9/5) + 32
        R = humidity

        HI = (
            -42.379 +
            2.04901523 * T +
            10.14333127 * R -
            0.22475541 * T * R -
            0.00683783 * T * T -
            0.05481717 * R * R +
            0.00122874 * T * T * R +
            0.00085282 * T * R * R -
            0.00000199 * T * T * R * R
        )

        # Convert back to Celsius
        return (HI - 32) * 5/9

    df["heat_index"] = df.apply(
        lambda row: calculate_heat_index(
            row["temperature_celsius"], row["humidity"]
        ),
        axis=1
    )
    
    
    
        # -------------------------------
    # Wind Chill (Feels Cold Temp)
    # Valid for temp <= 10°C and wind > 4.8 km/h
    # -------------------------------
    def calculate_wind_chill(temp_c, wind_kph):
        if pd.isna(temp_c) or pd.isna(wind_kph):
            return np.nan
        if temp_c > 10 or wind_kph < 4.8:
            return temp_c

        v = wind_kph ** 0.16
        wc = 13.12 + 0.6215 * temp_c - 11.37 * v + 0.3965 * temp_c * v
        return wc

    df["wind_chill"] = df.apply(
        lambda row: calculate_wind_chill(
            row["temperature_celsius"], row["wind_kph"]
        ),
        axis=1
    )
    
    
# numeric safety
    num_cols = [
        "temperature_celsius",
        "humidity",
        "wind_kph",
        "precip_mm",
        "air_quality_PM2.5"
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # derived
    df["month"] = df["last_updated"].dt.month
    df["year"] = df["last_updated"].dt.year

    # ---------- SEASON (SAFE FUNCTION) ----------
    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Autumn"
        else:
            return np.nan

    df["season"] = df["month"].apply(get_season)

    # ---------- CLIMATE ZONE (GUARANTEED COLUMN) ----------
    if "latitude" in df.columns:
        df["climate_zone"] = pd.cut(
            df["latitude"].astype(float),
            bins=[-90, -23.5, 23.5, 90],
            labels=["Southern Temperate", "Tropical", "Northern Temperate"]
        )
    else:
        df["climate_zone"] = "Unknown"

    return df

df = load_data()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("🎛 Dashboard Controls")

# ---------- Filters ----------
zones = df["climate_zone"].dropna().unique().tolist()
selected_zones = st.sidebar.multiselect(
    "Climate Zones",
    zones,
    default=zones
)

seasons = df["season"].dropna().unique().tolist()
selected_seasons = st.sidebar.multiselect(
    "Seasons",
    seasons,
    default=seasons
)

temp_min, temp_max = st.sidebar.slider(
    "Temperature Range (°C)",
    int(df["temperature_celsius"].min()),
    int(df["temperature_celsius"].max()),
    (10, 30)
)

highlight_extremes = st.sidebar.checkbox(
    "Highlight Extreme Events", value=True
)

normalize_data = st.sidebar.checkbox(
    "Normalize Data for Comparison", value=False
)

# ---------- Aggregation ----------
st.sidebar.subheader("📊 Time Aggregation")

aggregation = st.sidebar.selectbox(
    "Aggregation Level",
    ["Daily", "7-Day Moving Average", "Monthly"]
)


# ---------- APPLY FILTERS ----------
filtered_df = df[
    (df["climate_zone"].isin(selected_zones)) &
    (df["season"].isin(selected_seasons)) &
    (df["temperature_celsius"].between(temp_min, temp_max))
]
# ---------- APPLY AGGREGATION ----------
plot_df = filtered_df.copy()

if aggregation == "7-Day Moving Average":
    plot_df = (
        plot_df
        .set_index("last_updated")
        .sort_index()
        .groupby("country")
        .rolling("7D")["temperature_celsius"]
        .mean()
        .reset_index()
    )

elif aggregation == "Monthly":
    plot_df = (
        plot_df
        .groupby(
            [plot_df["last_updated"].dt.to_period("M"), "country"]
        )["temperature_celsius"]
        .mean()
        .reset_index()
    )
    plot_df["last_updated"] = plot_df["last_updated"].dt.to_timestamp()



# ---------- EXPORT ----------
st.sidebar.divider()
st.sidebar.subheader("📥 Export Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="⬇️ Download Analysis Report (CSV)",
    data=csv,
    file_name="climatescope_milestone3_report.csv",
    mime="text/csv"
)




# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#60a5fa;'>
🔵 Global Weather Data Analysis Dashboard
</h1>
""", unsafe_allow_html=True)


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Average Temperature", f"{filtered_df['temperature_celsius'].mean():.1f}°C")
c2.metric("Extreme Events Detected", filtered_df[filtered_df["temperature_celsius"] > 40].shape[0])
c3.metric("Average Humidity", f"{filtered_df['humidity'].mean():.0f}%")
c4.metric("Avg PM2.5", f"{filtered_df['air_quality_PM2.5'].mean():.0f}")

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌍 Global Overview",
    "📊 Statistical Analysis",
    "⚠ Extreme Events",
    "🌐 Regional Analysis",
    "⏱ Time Patterns",
    "❓ Help & User Guide"
])


# --------------------------------------------------
# TAB 1
# --------------------------------------------------
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        fig_map = px.scatter_geo(
            filtered_df,
            lat="latitude",
            lon="longitude",
            color="temperature_celsius",
            hover_name="country",
            color_continuous_scale="RdYlBu_r",
            title="Global Temperature Distribution"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        hottest = filtered_df.groupby("country")["temperature_celsius"].mean().sort_values(ascending=False).head(5)
        st.dataframe(hottest.reset_index(), use_container_width=True)

# --------------------------------------------------
# TAB 2
# --------------------------------------------------
with tab2:
    st.markdown("## 🔑 Key Weather Indicators")

    # seaborn theme
    sns.set_theme(style="darkgrid")

    fig, ax = plt.subplots(2, 2, figsize=(15, 9))
    fig.patch.set_facecolor("#0e1117")  # dark background

    for row in ax:
        for a in row:
            a.set_facecolor("#0e1117")
            a.tick_params(colors="white")
            a.title.set_color("white")
            a.xaxis.label.set_color("white")
            a.yaxis.label.set_color("white")

    # 🌡 Temperature
    sns.histplot(
        filtered_df["temperature_celsius"].dropna(),
        bins=25,
        kde=True,
        color="#ff7f50",
        edgecolor="black",
        linewidth=0.6,
        ax=ax[0, 0]
    )
    ax[0, 0].set_title("🌡 Temperature Distribution (°C)", fontsize=12, weight="bold")

    # 💧 Humidity
    sns.histplot(
        filtered_df["humidity"].dropna(),
        bins=25,
        kde=True,
        color="#4fc3f7",
        edgecolor="black",
        linewidth=0.6,
        ax=ax[0, 1]
    )
    ax[0, 1].set_title("💧 Humidity Distribution (%)", fontsize=12, weight="bold")

    # 🌬 Wind
    sns.histplot(
        filtered_df["wind_kph"].dropna(),
        bins=25,
        kde=True,
        color="#81c784",
        edgecolor="black",
        linewidth=0.6,
        ax=ax[1, 0]
    )
    ax[1, 0].set_title("🌬 Wind Speed Distribution (kph)", fontsize=12, weight="bold")

    # 🏭 Air Quality
    if "air_quality_PM2.5" in filtered_df.columns:
        sns.histplot(
            filtered_df["air_quality_PM2.5"].dropna(),
            bins=25,
            kde=True,
            color="#ffd54f",
            edgecolor="black",
            linewidth=0.6,
            ax=ax[1, 1]
        )
        ax[1, 1].set_title("🏭 Air Quality (PM2.5) Distribution", fontsize=12, weight="bold")

    plt.tight_layout(pad=2)
    st.pyplot(fig)

    st.markdown("---")



    st.markdown("### Correlation Analysis")

    corr_cols = [
        "temperature_celsius",
        "humidity",
        "wind_kph",
        "precip_mm",
        "air_quality_PM2.5"
    ]

    corr_df = filtered_df[corr_cols].dropna()

    if not corr_df.empty:
        corr = corr_df.corr()

        # dark theme setup
        sns.set_theme(style="dark")

        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")

        sns.heatmap(
            corr,
            cmap="coolwarm",
            center=0,
            annot=True,
            fmt=".2f",
            annot_kws={
                "size": 8,
                "color": "white"
            },
            linewidths=0.4,
            linecolor="#2a2a2a",
            cbar_kws={
                "shrink": 0.8
            },
            ax=ax
        )

        ax.set_title(
            "Correlation Between Climate Variables",
            fontsize=11,
            fontweight="medium",
            color="white",
            pad=10
        )

        ax.tick_params(axis="x", colors="white", labelsize=8, rotation=35)
        ax.tick_params(axis="y", colors="white", labelsize=8)

        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.info("Not enough data available for correlation analysis.")
        
    # --------------------------------------------------
    # VIOLIN PLOT (Season-wise Temperature Distribution)
    # --------------------------------------------------
    st.markdown("### 🎻 Temperature Distribution by Season")

    fig_violin = px.violin(
        filtered_df,
        y="temperature_celsius",
        x="season",
        color="season",
        box=True,
        points="outliers",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_violin.update_layout(
        template="plotly_dark",
        height=420,
        title={
            "text": "Season-wise Temperature Distribution",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 14}
        },
        xaxis_title="Season",
        yaxis_title="Temperature (°C)",
        showlegend=False
    )

    st.plotly_chart(fig_violin, use_container_width=True)





with tab3:
    st.markdown("## ⚠ Extreme Weather Events")

    extreme_df = filtered_df[
        (filtered_df["temperature_celsius"] > 40) |
        (filtered_df["wind_kph"] > 50) |
        (filtered_df["precip_mm"] > 100)
    ]

    st.markdown("### 🔥 Top Extreme Events")
    st.dataframe(extreme_df.head(10), use_container_width=True)

    if not extreme_df.empty:
        monthly_extreme = (
            extreme_df
            .groupby(extreme_df["last_updated"].dt.to_period("M"))
            .size()
            .reset_index(name="Extreme Events")
        )
        monthly_extreme["last_updated"] = monthly_extreme["last_updated"].dt.to_timestamp()

        fig_ext = px.line(
            monthly_extreme,
            x="last_updated",
            y="Extreme Events",
            markers=True,
            title="Monthly Extreme Events Trend",
            template="plotly_dark"
        )

        st.plotly_chart(fig_ext, use_container_width=True)
    else:
        st.info("No extreme events detected for selected filters.")



# --------------------------------------------------
# TAB 4
# --------------------------------------------------
with tab4:
    fig_region = px.box(
        filtered_df,
        x="climate_zone",
        y="temperature_celsius",
        color="climate_zone"
    )
    st.plotly_chart(fig_region, use_container_width=True)

# --------------------------------------------------
# TAB 5
# --------------------------------------------------
with tab5:
    fig_trend = px.line(
    plot_df,
    x="last_updated",
    y="temperature_celsius",
    color="country",
    title=f"Temperature Trend ({aggregation})"
)



   
    st.plotly_chart(fig_trend, use_container_width=True)
    
        # ---------- AREA CHART ----------
    st.subheader("🌡 Temperature Trend (Area Chart)")

    fig_area = px.area(
        plot_df,
        x="last_updated",
        y="temperature_celsius",
        color="country",
        title=f"Temperature Trend – Area View ({aggregation})",
    
    )
    fig_area.update_traces(opacity=0.6)

    st.plotly_chart(fig_area, use_container_width=True)



st.write(df[["temperature_celsius", "humidity", "heat_index", "wind_chill"]].head())



with tab6:
    st.markdown("## ❓ User Guide")

    st.markdown("""
### 🎛 Controls
- Filter by climate zone, season, and temperature
- Choose aggregation: Daily / 7-Day / Monthly

### 📊 Visuals
- Line & Area charts show trends
- Violin & histograms show distributions
- Heatmap shows correlations
- Maps show geographic spread

### ⚠ Extreme Events
- Heatwave > 40°C
- Heavy rain > 100 mm
- High wind > 50 kph

### 📥 Export
- CSV export available in sidebar
    """)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
