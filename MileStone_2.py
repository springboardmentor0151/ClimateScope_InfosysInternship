import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Climate Scope Dashboard",
    layout="wide"
)

st.title(" CLIMATE SCOPE ANALYSIS")

# ----------------------------
# LOAD DATA
# ----------------------------
uploaded = st.file_uploader("Upload Climate Data CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    # Clean and normalize column names to avoid KeyErrors
    df.columns = df.columns.str.strip().str.lower()

    # Helper: safe column getter
    def safe_col(target):
        target = target.lower()
        for col in df.columns:
            if target in col:
                return col
        return None

    # Resolve air quality columns safely
    col_carbon   = safe_col("air_quality_carbon") or safe_col("carbon")
    col_nitrogen = safe_col("air_quality_nitrogen") or safe_col("nitrogen")
    col_ozone    = safe_col("air_quality_ozone") or safe_col("ozone")

    # ------------------------------------------------------
    # SIDEBAR FILTERS (NEW)
    # ------------------------------------------------------
    st.sidebar.header(" Filters")

    country_filter  = st.sidebar.multiselect("Country", df[safe_col("country")].unique() if safe_col("country") else [])
    season_filter   = st.sidebar.multiselect("Season", df[safe_col("season")].unique() if safe_col("season") else [])
    timezone_filter = st.sidebar.multiselect("Timezone", df[safe_col("timezone")].unique() if safe_col("timezone") else [])

    # Apply filters
    filtered_df = df.copy()

    if country_filter:
        filtered_df = filtered_df[filtered_df[safe_col("country")].isin(country_filter)]
    if season_filter:
        filtered_df = filtered_df[filtered_df[safe_col("season")].isin(season_filter)]
    if timezone_filter:
        filtered_df = filtered_df[filtered_df[safe_col("timezone")].isin(timezone_filter)]

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Count of Country", filtered_df[safe_col("country")].nunique() if safe_col("country") else "N/A")

    with col2:
        st.metric("Count of Location Name", filtered_df[safe_col("location_name")].nunique() if safe_col("location_name") else "N/A")

    with col3:
        st.metric("Avg Air Quality (Carbon)", 
                   round(filtered_df[col_carbon].mean(), 2) if col_carbon else "N/A")

    with col4:
        st.metric("Avg Air Quality (Nitrogen)", 
                   round(filtered_df[col_nitrogen].mean(), 2) if col_nitrogen else "N/A")

    with col5:
        st.metric("Avg Air Quality (Ozone)", 
                   round(filtered_df[col_ozone].mean(), 2) if col_ozone else "N/A")

    # ------------------------------------------------------
    # ORIGINAL VISUALIZATIONS
    # ------------------------------------------------------
    st.subheader("Average Humidity by Location Name")

    if safe_col("humidity") and safe_col("location_name"):
        fig1 = px.bar(
            filtered_df.groupby(safe_col("location_name"))[safe_col("humidity")]
            .mean()
            .sort_values(ascending=False)
            .head(10),
            orientation="h"
        )
        st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Count of Country by Timezone")
    if safe_col("timezone") and safe_col("country"):
        fig2 = px.bar(
            filtered_df.groupby(safe_col("timezone"))[safe_col("country")]
            .count()
            .sort_values(ascending=False)
            .head(10),
            orientation="h"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Count of Country by Season")
    if safe_col("season"):
        fig3 = px.pie(
            filtered_df,
            names=safe_col("season"),
            hole=0
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Max Temperature by Location")
    if safe_col("location") and safe_col("max_temp_celsius"):
        fig4 = px.bar(
            filtered_df.groupby(safe_col("location"))[safe_col("max_temp_celsius")]
            .max()
            .sort_values(ascending=False)
            .head(20)
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Wind Speed & Hour by Wind Direction")
    if safe_col("wind_direction") and safe_col("wind_kph") and safe_col("hour"):
        wind_df = filtered_df.groupby(safe_col("wind_direction")).agg({
            safe_col("wind_kph"): "mean",
            safe_col("hour"): "mean"
        }).reset_index()

        fig5 = px.line(
            wind_df,
            x=safe_col("wind_direction"),
            y=[safe_col("wind_kph"), safe_col("hour")]
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Condition Text Count")
    if safe_col("condition_text"):
        fig6 = px.pie(filtered_df, names=safe_col("condition_text"), hole=0.4)
        st.plotly_chart(fig6, use_container_width=True)

    # ------------------------------------------------------
    # 📊 NEW ADVANCED ANALYTICS & VISUALIZATIONS
    # ------------------------------------------------------

    st.header("Climate Analytics")

    # 1. Temperature Trend Over Time ------------------------
    if safe_col("date") and safe_col("temp_celsius"):
        st.subheader("Temperature Trend Over Time")
        filtered_df[safe_col("date")] = pd.to_datetime(filtered_df[safe_col("date")])

        fig7 = px.line(
            filtered_df.sort_values(safe_col("date")),
            x=safe_col("date"),
            y=safe_col("temp_celsius"),
            color=safe_col("country"),
            markers=True
        )
        st.plotly_chart(fig7, use_container_width=True)

    # 2. Correlation Heatmap --------------------------------
    st.subheader("Correlation Heatmap (Climate Variables)")
    numeric_df = filtered_df.select_dtypes(include='number').corr()

    fig8 = px.imshow(
        numeric_df,
        color_continuous_scale="Viridis",
        text_auto=True,
        aspect="auto"
    )
    st.plotly_chart(fig8, use_container_width=True)

    # 3. Humidity vs Temperature Scatter ---------------------
    if safe_col("humidity") and safe_col("temp_celsius"):
        st.subheader("Humidity vs Temperature (with Trendline)")
        fig9 = px.scatter(
            filtered_df,
            x=safe_col("humidity"),
            y=safe_col("temp_celsius"),
            trendline="ols",
            color=safe_col("country") if safe_col("country") else None
        )
        st.plotly_chart(fig9, use_container_width=True)

    # 4. Wind Speed Distribution -----------------------------
    if safe_col("wind_kph"):
        st.subheader("Wind Speed Distribution")
        fig10 = px.histogram(
            filtered_df,
            x=safe_col("wind_kph"),
            nbins=40,
            color=safe_col("country") if safe_col("country") else None
        )
        st.plotly_chart(fig10, use_container_width=True)

    # 5. Season-wise Temperature Comparison ------------------
    if safe_col("season") and safe_col("temp_celsius"):
        st.subheader("Season-wise Temperature Distribution")
        fig11 = px.box(
            filtered_df,
            x=safe_col("season"),
            y=safe_col("temp_celsius"),
            color=safe_col("season")
        )
        st.plotly_chart(fig11, use_container_width=True)

    # 6. Air Quality Comparison ------------------------------
    if col_carbon and col_nitrogen and col_ozone:
        st.subheader("Air Quality Comparison (Carbon vs Nitrogen vs Ozone)")
        aq_df = filtered_df[[col_carbon, col_nitrogen, col_ozone]]

        fig12 = px.line(aq_df, markers=True)
        st.plotly_chart(fig12, use_container_width=True)

    # 7. Climate Choropleth Map ------------------------------
    st.subheader("Climate Temperature Map by Country")

    if safe_col("country") and safe_col("temp_celsius"):
        fig13 = px.choropleth(
            filtered_df,
            locations=safe_col("country"),
            locationmode='country names',
            color=safe_col("temp_celsius"),
            color_continuous_scale="Turbo"
        )
        st.plotly_chart(fig13, use_container_width=True)

    # ------------------------------------------------------
    # Bottom KPIs (Original)
    # ------------------------------------------------------
 # ----------------------------
# UNIVERSAL TEMPERATURE KPI HANDLER
# ----------------------------

# Possible matches for different data sources
min_candidates = ["min_temp", "mintemp", "minimum_temperature"]
avg_candidates = ["temp", "temperature", "avg_temp", "average_temp"]
max_candidates = ["max_temp", "maxtemp", "maximum_temperature"]

def find_column(candidates):
    for c in candidates:
        match = safe_col(c)
        if match:
            return match
    return None

col_min_temp = find_column(min_candidates)
col_avg_temp = find_column(avg_candidates)
col_max_temp = find_column(max_candidates)

c1, c2, c3 = st.columns(3)

with c1:
    if col_min_temp:
        st.metric("Min Temp Celsius", round(filtered_df[col_min_temp].min(), 2))
    else:
        st.metric("Min Temp Celsius", "N/A")

with c2:
    if col_avg_temp:
        st.metric("Avg Temp Celsius", round(filtered_df[col_avg_temp].mean(), 2))
    else:
        st.metric("Avg Temp Celsius", "N/A")

with c3:
    if col_max_temp:
        st.metric("Max Temp Celsius", round(filtered_df[col_max_temp].max(), 2))
    else:
        st.metric("Max Temp Celsius", "N/A")
