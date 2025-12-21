import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(page_title="ClimateScope — Milestone 2",
                   layout="wide")

# Custom CSS for beautification
st.markdown("""
<style>
body {
    background-color: #0f1117;
    color: #ffffff;
}
.big-title {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(to right, #4FACFE, #00F2FE);
    -webkit-background-clip: text;
    color: transparent;
    text-align: center;
    padding: 10px;
}
.section-title {
    font-size: 28px;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 10px;
    color: #78c8ff;
}
.metric-card {
    padding: 18px;
    border-radius: 15px;
    background: #1b1e27;
    box-shadow: 0px 0px 10px rgba(255,255,255,0.05);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------
# LOAD DATA
# ------------------------------------------
df = pd.read_csv("data/processed/cleaned_weather.csv")
df['date'] = pd.to_datetime(df['last_updated'], errors='coerce')
# Find countries for the extreme metrics
hottest_country = df.loc[df['temperature_celsius'].idxmax(), 'country']
coldest_country = df.loc[df['temperature_celsius'].idxmin(), 'country']
humid_country = df.loc[df['humidity'].idxmax(), 'country']
rain_country = df.loc[df['precip_mm'].idxmax(), 'country']


# ------------------------------------------
# BEAUTIFUL HEADER
# ------------------------------------------
st.markdown("<h1 class='big-title'>ClimateScope – Milestone 2 Dashboard</h1>", unsafe_allow_html=True)
st.write("### Live Global Weather Snapshot — Country-based Analysis")

# ------------------------------------------
# TOP METRICS
# ------------------------------------------
colA, colB, colC, colD = st.columns(4)

with colA:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Max Temperature (°C)", 
              f"{df['temperature_celsius'].max():.1f}", 
              f"{hottest_country}")
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Min Temperature (°C)", 
              f"{df['temperature_celsius'].min():.1f}", 
              f"{coldest_country}")
    st.markdown("</div>", unsafe_allow_html=True)

with colC:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Max Humidity (%)", 
              f"{df['humidity'].max():.0f}", 
              f"{humid_country}")
    st.markdown("</div>", unsafe_allow_html=True)

with colD:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Max Rainfall (mm)", 
              f"{df['precip_mm'].max():.1f}", 
              f"{rain_country}")
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("---")

# --------------------------------------------------------------
# SECTION 1: TEMPERATURE BY COUNTRY
# --------------------------------------------------------------
st.markdown("<h2 class='section-title'>🌡️ Temperature by Country (°C)</h2>", unsafe_allow_html=True)

temp_sorted = df.sort_values("temperature_celsius", ascending=False)

fig_temp = px.bar(
    temp_sorted.head(20),
    x="country",
    y="temperature_celsius",
    color="temperature_celsius",
    color_continuous_scale="redor",
    title="Top 20 Hottest Countries",
)
st.plotly_chart(fig_temp, use_container_width=True)

# --------------------------------------------------------------
# SECTION 2: RAINFALL BY COUNTRY
# --------------------------------------------------------------
st.markdown("<h2 class='section-title'>🌧 Rainfall by Country (mm)</h2>", unsafe_allow_html=True)

rain_sorted = df.sort_values("precip_mm", ascending=False)

fig_rain = px.bar(
    rain_sorted.head(20),
    x="country",
    y="precip_mm",
    color="precip_mm",
    color_continuous_scale="blues",
    title="Top Rainfall Countries",
)
st.plotly_chart(fig_rain, use_container_width=True)

# --------------------------------------------------------------
# SECTION 3: TEMP VS HUMIDITY SCATTER
# --------------------------------------------------------------
st.markdown("<h2 class='section-title'>🔥 Temperature vs Humidity</h2>", unsafe_allow_html=True)

fig_scatter = px.scatter(
    df,
    x="temperature_celsius",
    y="humidity",
    color="country",
    hover_name="country",
    title="How Temperature relates to Humidity",
    opacity=0.7
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --------------------------------------------------------------
# SECTION 4: EXTREME WEATHER TABLE
# --------------------------------------------------------------
st.markdown("<h2 class='section-title'>⚠️ Extreme Weather Events</h2>", unsafe_allow_html=True)

extreme = df[
    (df["temperature_celsius"] > 40) |
    (df["precip_mm"] > 100) |
    (df["wind_kph"] > 50)
]

if len(extreme) == 0:
    st.info("No extreme weather detected today.")
else:
    st.dataframe(extreme)

# --------------------------------------------------------------
# SECTION 5: STATS SUMMARY
# --------------------------------------------------------------
st.markdown("<h2 class='section-title'>📊 Statistical Summary</h2>", unsafe_allow_html=True)

stats = df[['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']].describe().T
st.dataframe(stats)
