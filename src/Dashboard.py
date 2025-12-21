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

# ---------- APPLY FILTERS ----------
filtered_df = df[
    (df["climate_zone"].isin(selected_zones)) &
    (df["season"].isin(selected_seasons)) &
    (df["temperature_celsius"].between(temp_min, temp_max))
]

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
# FILTER DATA
# --------------------------------------------------
filtered_df = df[
    (df["climate_zone"].isin(selected_zones)) &
    (df["season"].isin(selected_seasons)) &
    (df["temperature_celsius"].between(temp_min, temp_max))
]

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Global Overview",
    "📊 Statistical Analysis",
    "⚠ Extreme Events",
    "🌐 Regional Analysis",
    "⏱ Time Patterns"
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
    trend = filtered_df.groupby("month")["temperature_celsius"].mean().reset_index()
    fig_trend = px.line(trend, x="month", y="temperature_celsius")
    st.plotly_chart(fig_trend, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
