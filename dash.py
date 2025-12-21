import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="ClimateScope Dashboard",
    layout="wide"
)

# =====================================================
# LOAD & PREPARE DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_weather.csv")
    df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
    df = df.dropna(subset=['last_updated'])

    df['year'] = df['last_updated'].dt.year
    df['month'] = df['last_updated'].dt.month
    df['month_name'] = df['last_updated'].dt.strftime('%b')

    return df

df = load_data()

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.title("🌍 ClimateScope Filters")

countries = st.sidebar.multiselect(
    "Select Country",
    options=df['country'].unique(),
    default=df['country'].unique()[:5]
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df['last_updated'].min(), df['last_updated'].max()]
)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["temperature_celsius", "humidity", "precip_mm", "wind_kph"]
)

threshold = st.sidebar.slider(
    "Extreme Threshold",
    float(df[metric].min()),
    float(df[metric].max()),
    float(df[metric].quantile(0.95))
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Statistical Analysis",
        "Climate Trends",
        "Extreme Events",
        "Help"
    ]
)

# =====================================================
# APPLY FILTERS
# =====================================================
filtered = df[
    (df['country'].isin(countries)) &
    (df['last_updated'].between(
        pd.to_datetime(date_range[0]),
        pd.to_datetime(date_range[1])
    ))
]

# =====================================================
# EXECUTIVE DASHBOARD
# =====================================================
if page == "Executive Dashboard":
    st.title("🌎 ClimateScope – Executive Dashboard")

    # KPI CARDS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average", round(filtered[metric].mean(), 2))
    c2.metric("Maximum", round(filtered[metric].max(), 2))
    c3.metric("Minimum", round(filtered[metric].min(), 2))
    c4.metric("Records", len(filtered))

    # TODAY SNAPSHOT
    st.subheader("📌 Latest Weather Snapshot")
    latest = filtered.sort_values("last_updated").iloc[-1]

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Temp (°C)", round(latest["temperature_celsius"], 2))
    s2.metric("Humidity (%)", round(latest["humidity"], 2))
    s3.metric("Rain (mm)", round(latest["precip_mm"], 2))
    s4.metric("Wind (kph)", round(latest["wind_kph"], 2))

    # GLOBAL MAP
    st.subheader("🗺️ Global Weather Map")
    fig_map = px.scatter_geo(
        filtered,
        lat="latitude",
        lon="longitude",
        color=metric,
        hover_name="country",
        animation_frame="year",
        projection="natural earth"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # TIME SERIES
    st.subheader("📈 Time-Series Trend")
    ts = filtered.groupby("last_updated")[metric].mean().reset_index()
    fig_ts = px.line(ts, x="last_updated", y=metric)
    st.plotly_chart(fig_ts, use_container_width=True)

# =====================================================
# STATISTICAL ANALYSIS
# =====================================================
elif page == "Statistical Analysis":
    st.title("📊 Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig_scatter = px.scatter(
            filtered,
            x="humidity",
            y="temperature_celsius",
            color="country",
            title="Temperature vs Humidity"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        corr = filtered[
            ["temperature_celsius", "humidity", "precip_mm", "wind_kph"]
        ].corr()
        fig_heat = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
        st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("📋 Descriptive Statistics")
    st.dataframe(filtered.describe())

    st.subheader("📊 Distribution Analysis")
    d1, d2 = st.columns(2)

    with d1:
        fig_hist = px.histogram(filtered, x=metric, nbins=30, title="Histogram")
        st.plotly_chart(fig_hist, use_container_width=True)

    with d2:
        fig_box = px.box(filtered, y=metric, title="Box Plot")
        st.plotly_chart(fig_box, use_container_width=True)

# =====================================================
# CLIMATE TRENDS
# =====================================================
elif page == "Climate Trends":
    st.title("🌡️ Climate Trends")

    monthly = (
        filtered.groupby("month_name")[metric]
        .mean()
        .reindex(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    )

    fig_line = px.line(
        x=monthly.index,
        y=monthly.values,
        labels={"x": "Month", "y": metric},
        title="Monthly Average Trend"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    fig_box_country = px.box(
        filtered,
        x="country",
        y=metric,
        title="Metric Distribution by Country"
    )
    st.plotly_chart(fig_box_country, use_container_width=True)

# =====================================================
# EXTREME EVENTS
# =====================================================
elif page == "Extreme Events":
    st.title("🚨 Extreme Climate Events")

    extreme = filtered[filtered[metric] >= threshold]

    if extreme.empty:
        st.warning("No extreme events detected for selected threshold.")
    else:
        st.subheader("🔥 Extreme Events Frequency by Country")
        freq = extreme.groupby("country")[metric].count().reset_index()
        fig_freq = px.bar(freq, x="country", y=metric)
        st.plotly_chart(fig_freq, use_container_width=True)

        st.subheader("🏆 Top 5 Extreme Events")
        st.dataframe(
            extreme.sort_values(metric, ascending=False)
            .head(5)[["country", "last_updated", metric]]
        )

# =====================================================
# HELP PAGE
# =====================================================
else:
    st.title("❓ Help & User Guide")
    st.markdown("""
    **ClimateScope Dashboard**

    - Use sidebar filters to select countries, date range, and metric  
    - Navigate pages using radio buttons  
    - Hover on charts for details  
    - Zoom and pan using Plotly tools  
    - Download filtered data from sidebar  
    """)

# =====================================================
# DOWNLOAD DATA
# =====================================================
st.sidebar.download_button(
    "⬇️ Download Filtered Data",
    filtered.to_csv(index=False),
    file_name="filtered_climate_data.csv",
    mime="text/csv"
)
