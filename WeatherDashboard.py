import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- DATA LOADING --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("GlobalWeatherCleaned.csv")  # TODO: change to your real path
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    return df

df = load_data()

metrics = [
    "temperature_celsius",
    "humidity",
    "precip_mm",
    "wind_kph",
    "uv_index",
    "air_quality_PM2.5",
]

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Global Weather & Air Quality Dashboard",
    layout="wide",
)

st.title("🌍 Global Weather & Air Quality Dashboard")
st.caption("Interactive dashboard for Core Analysis & Visualization Design")

# -------------------- SIDEBAR: GLOBAL CONTROLS --------------------
st.sidebar.header("Global Filters")

all_countries = sorted(df["country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=all_countries,
    default=all_countries[:5],
)

min_date = df["last_updated"].min()
max_date = df["last_updated"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

selected_metric = st.sidebar.selectbox(
    "Primary metric",
    options=metrics,
    index=0,
)

page_mode = st.sidebar.radio(
    "Dashboard mode",
    options=["Overview", "Extreme Events", "Regional Comparison"],
)

st.sidebar.markdown("---")

# Filter data once, use everywhere
filtered = df.copy()
if selected_countries:
    filtered = filtered[filtered["country"].isin(selected_countries)]

start_date, end_date = date_range
filtered = filtered[
    (filtered["last_updated"].dt.date >= start_date)
    & (filtered["last_updated"].dt.date <= end_date)
]

# -------------------- OVERVIEW MODE --------------------
if page_mode == "Overview":
    st.subheader("📌 Overview")

    # KPI row
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Avg Temperature (°C)", f"{filtered['temperature_celsius'].mean():.1f}")
    with k2:
        st.metric("Avg Humidity (%)", f"{filtered['humidity'].mean():.1f}")
    with k3:
        st.metric("Avg PM2.5 (µg/m³)", f"{filtered['air_quality_PM2.5'].mean():.1f}")

    st.markdown("---")

    # Chart controls
    chart_col, country_focus_col = st.columns([2, 1])

    with chart_col:
        chart_type = st.selectbox(
            "Time-series chart type",
            options=["Line", "Area", "Bar"],
            index=0,
        )

        ts = (
            filtered
            .set_index("last_updated")
            .resample("D")[selected_metric]
            .mean()
            .reset_index()
        )

        st.markdown(f"### {selected_metric} over time")

        if ts.empty:
            st.info("No data for current filters.")
        else:
            if chart_type == "Line":
                fig_ts = px.line(ts, x="last_updated", y=selected_metric)
            elif chart_type == "Area":
                fig_ts = px.area(ts, x="last_updated", y=selected_metric)
            else:  # Bar
                fig_ts = px.bar(ts, x="last_updated", y=selected_metric)

            fig_ts.update_layout(
                xaxis_title="Date",
                yaxis_title=selected_metric,
                hovermode="x unified",
            )
            st.plotly_chart(fig_ts, use_container_width=True)

    with country_focus_col:
        st.markdown("### 🔍 Country focus")
        focus_country = st.selectbox(
            "Select a country to inspect",
            options=["(none)"] + selected_countries,
        )
        if focus_country != "(none)":
            sub = filtered[filtered["country"] == focus_country]
            st.write(f"Records for **{focus_country}**: {len(sub)}")
            st.write(
                sub[
                    ["last_updated", "location_name"] + metrics
                ].sort_values("last_updated").tail(10)
            )

    st.markdown("---")

    # Tabs for extra views
    tab1, tab2 = st.tabs(["Top countries by metric", "Data preview"])

    with tab1:
        st.markdown(f"#### 🌎 Top 10 countries by {selected_metric}")
        country_agg = (
            filtered.groupby("country")[selected_metric]
            .mean()
            .reset_index()
            .sort_values(selected_metric, ascending=False)
            .head(10)
        )
        if country_agg.empty:
            st.info("No data for current filters.")
        else:
            fig_bar = px.bar(
                country_agg,
                x="country",
                y=selected_metric,
                labels={"country": "Country", selected_metric: selected_metric},
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.markdown("#### Filtered data")
        st.dataframe(
            filtered[["last_updated", "country", "location_name"] + metrics].head(500),
            use_container_width=True,
        )
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download filtered data as CSV",
            data=csv,
            file_name="filtered_weather_data.csv",
            mime="text/csv",
        )

# -------------------- EXTREME EVENTS MODE --------------------
elif page_mode == "Extreme Events":
    st.subheader("⚠️ Extreme Events Explorer")

    st.caption(
        "Define extreme events as values above a chosen percentile (e.g., top 5% or 10%)."
    )

    percentile = st.slider(
        "Select percentile threshold for extremes (higher = more rare)",
        min_value=80,
        max_value=99,
        value=95,
        step=1,
    )

    thresh = filtered[metrics].quantile(percentile / 100.0)

    st.write("Current thresholds:")
    st.write(thresh.to_frame("threshold").style.format("{:.2f}"))

    # Mark extremes
    extremes = []
    for m in metrics:
        mask = filtered[m] >= thresh[m]
        temp = filtered.loc[mask, ["last_updated", "country", "location_name", m]].copy()
        temp["metric"] = m
        temp["value"] = temp[m]
        temp = temp.drop(columns=[m])
        extremes.append(temp)

    extreme_events = pd.concat(extremes, ignore_index=True) if extremes else pd.DataFrame()

    if extreme_events.empty:
        st.info("No extreme events found for the current settings.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Counts by metric")
            metric_counts = (
                extreme_events["metric"]
                .value_counts()
                .rename_axis("metric")
                .reset_index(name="count")
            )
            fig_mc = px.bar(metric_counts, x="metric", y="count")
            st.plotly_chart(fig_mc, use_container_width=True)

        with col2:
            st.markdown("### Top 10 countries by extreme events")
            country_counts = (
                extreme_events.groupby("country")
                .size()
                .reset_index(name="num_events")
                .sort_values("num_events", ascending=False)
                .head(10)
            )
            fig_cc = px.bar(country_counts, x="country", y="num_events")
            fig_cc.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_cc, use_container_width=True)

        with st.expander("Show extreme events table"):
            st.dataframe(
                extreme_events.sort_values("last_updated", ascending=False).head(500),
                use_container_width=True,
            )

# -------------------- REGIONAL COMPARISON MODE --------------------
else:
    st.subheader("🌐 Regional Comparison")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("### Choropleth map (avg metric by country)")
        map_metric = st.selectbox(
            "Metric for map",
            options=metrics,
            index=0,
        )

        country_mean = (
            filtered.groupby("country")[map_metric]
            .mean()
            .reset_index()
            .rename(columns={map_metric: "value"})
        )

        if country_mean.empty:
            st.info("No data for current filters.")
        else:
            # NOTE: this assumes 'country' contains recognizable country names
            fig_map = px.choropleth(
                country_mean,
                locations="country",
                locationmode="country names",
                color="value",
                hover_name="country",
                color_continuous_scale="Viridis",
                labels={"value": map_metric},
                title=f"Average {map_metric} by Country",
            )
            st.plotly_chart(fig_map, use_container_width=True)

    with right:
        st.markdown("### Top 10 countries")
        country_top = (
            filtered.groupby("country")[selected_metric]
            .mean()
            .reset_index()
            .sort_values(selected_metric, ascending=False)
            .head(10)
        )
        if country_top.empty:
            st.info("No data for current filters.")
        else:
            fig_top = px.bar(
                country_top,
                x="country",
                y=selected_metric,
                labels={"country": "Country", selected_metric: selected_metric},
            )
            fig_top.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    st.markdown("### Metric vs Country Heatmap (relative view)")
    country_mean_all = (
        filtered.groupby("country")[metrics]
        .mean()
        .reset_index()
    )

    if country_mean_all.empty:
        st.info("Not enough data to build heatmap.")
    else:
        norm = country_mean_all.copy()
        for m in metrics:
            col_min = norm[m].min()
            col_max = norm[m].max()
            norm[m] = (norm[m] - col_min) / (col_max - col_min + 1e-9)

        heat_df = norm.set_index("country")

        fig_heat = px.imshow(
            heat_df.T,
            labels=dict(x="Country", y="Metric", color="Relative intensity"),
            aspect="auto",
        )
        st.plotly_chart(fig_heat, use_container_width=True)