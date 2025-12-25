import datetime as dt

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------
# Page setup and styling
# ---------------------------------------------------------------------

st.set_page_config(page_title="Climatescope Weather Dashboard", layout="wide")

CUSTOM_CSS = """
<style>
.stApp {
    background: radial-gradient(circle at top left, #1e293b 0, #020617 55%, #020617 100%);
    color: #e5e7eb;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #020617;
    border-right: 1px solid #1f2937;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #e5e7eb;
}

/* Navigation radio */
div[role="radiogroup"] > label {
    background-color: #020617;
    border-radius: 999px;
    padding: 6px 16px;
    margin-right: 8px;
    border: 1px solid #1f2937;
}
div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(90deg, #22c55e, #0ea5e9);
    color: #020617 !important;
    border-color: transparent;
}

/* KPI cards */
div[data-testid="stMetric"] {
    background-color: #020617;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.7);
}

/* Plot containers */
.plot-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.85);
    margin-bottom: 1.5rem;
    background-color: #020617;
    padding: 0.75rem;
}

/* Text tweaks */
.stCaption, .stMarkdown p {
    color: #9ca3af;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def plot_block(fig):
    """Wrap Plotly charts in a styled container."""
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Data loading and derived metrics
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("Cleaned_Weather_Data.csv")
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    df = df.dropna(subset=["last_updated"])
    df["date"] = df["last_updated"].dt.date

    # Light ISO-3 mapping – extend for maps if needed
    iso_map = {
        "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA",
        "Andorra": "AND", "Angola": "AGO", "Argentina": "ARG",
        "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
        "Oman": "OMN", "Pakistan": "PAK", "Philippines": "PHL",
        "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT",
        "Romania": "ROU", "Peru": "PER", "Panama": "PAN",
    }
    df["iso_code"] = df["country"].map(iso_map)
    return df


def heat_index(temp_c, rh):
    T, R = temp_c, rh
    return (
        -8.78469475556
        + 1.61139411 * T
        + 2.33854883889 * R
        - 0.14611605 * T * R
        - 0.012308094 * T**2
        - 0.016424828 * R**2
        + 0.002211732 * T**2 * R
        + 0.00072546 * T * R**2
        - 0.000003582 * T**2 * R**2
    )


def wind_chill(temp_c, wind_kph):
    v, t = wind_kph, temp_c
    return 13.12 + 0.6215 * t - 11.37 * (v**0.16) + 0.3965 * t * (v**0.16)


def aggregate_time(data: pd.DataFrame, freq: str) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()
    by = data.set_index("last_updated").groupby(
        [pd.Grouper(freq=freq), "country"]
    )
    out = by.agg(
        {
            "temperature_celsius": "mean",
            "humidity": "mean",
            "precip_mm": "sum",
            "wind_kph": "mean",
        }
    ).reset_index()
    out.rename(columns={"last_updated": "period"}, inplace=True)
    return out


df = load_data()
df["heat_index"] = heat_index(df["temperature_celsius"], df["humidity"])
df["wind_chill"] = wind_chill(df["temperature_celsius"], df["wind_kph"])

# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------

st.sidebar.title("Filters")

countries = sorted(df["country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Country",
    countries,
    default=countries[:5] if len(countries) >= 5 else countries,
)

data_min = df["last_updated"].min().date()
data_max = df["last_updated"].max().date()
today = dt.date.today()

min_date = data_min
max_date = max(data_max, today)

default_start = max(data_min, today - dt.timedelta(days=30))
default_end = max_date

date_range = st.sidebar.date_input(
    "Date range",
    [default_start, default_end],
    min_value=min_date,
    max_value=max_date,
)

metric_options = {
    "Temperature (°C)": "temperature_celsius",
    "Humidity (%)": "humidity",
    "Precipitation (mm)": "precip_mm",
    "Wind speed (kph)": "wind_kph",
    "Heat index (°C)": "heat_index",
    "Wind chill (°C)": "wind_chill",
}
metric_label = st.sidebar.selectbox("Metric", list(metric_options.keys()))
metric = metric_options[metric_label]

threshold = st.sidebar.number_input(
    "Threshold for extreme events",
    value=float(df[metric].quantile(0.95)),
)

agg_label = st.sidebar.selectbox("Time aggregation", ["Daily", "Monthly", "Seasonal"])
freq_map = {"Daily": "D", "Monthly": "M", "Seasonal": "Q"}
agg_freq = freq_map[agg_label]

normalize = st.sidebar.checkbox("Normalize metric (z-score)", value=False)

# Handle single-date selection gracefully
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

mask = (
    df["country"].isin(selected_countries)
    & (df["date"] >= start_date)
    & (df["date"] <= end_date)
)
df_f = df[mask].copy()

if not df_f.empty:
    df_f["month"] = df_f["last_updated"].dt.to_period("M").astype(str)

    if normalize:
        z = (df_f[metric] - df_f[metric].mean()) / df_f[metric].std(ddof=0)
        df_f[f"{metric}_z"] = z
        metric_to_plot = f"{metric}_z"
    else:
        metric_to_plot = metric

    agg_df = aggregate_time(df_f, agg_freq)
else:
    metric_to_plot = metric
    agg_df = pd.DataFrame()

# ---------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------

st.title("Climatescope Weather Dashboard")

page = st.radio(
    "Navigate",
    [
        "Executive Dashboard",
        "Statistical Analysis",
        "Climate Trends",
        "Extreme Events",
        "Help",
    ],
    horizontal=True,
)

# ---------------------------------------------------------------------
# Executive Dashboard
# ---------------------------------------------------------------------

if page == "Executive Dashboard":
    if df_f.empty:
        st.info("No data for the selected filters. Try a 2023 date range from the dataset.")
    else:
        st.header("Executive Dashboard")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Mean Temp (°C)", f"{df_f['temperature_celsius'].mean():.1f}")
        k2.metric("Mean Humidity (%)", f"{df_f['humidity'].mean():.1f}")
        k3.metric("Total Precip (mm)", f"{df_f['precip_mm'].sum():.1f}")
        k4.metric("Mean Wind (kph)", f"{df_f['wind_kph'].mean():.1f}")

        st.subheader("Latest Weather Snapshot")
        latest_ts = df_f["last_updated"].max()
        latest_rows = df_f[df_f["last_updated"] == latest_ts]
        st.dataframe(
            latest_rows[
                [
                    "country",
                    "location_name",
                    "temperature_celsius",
                    "humidity",
                    "precip_mm",
                    "wind_kph",
                ]
            ]
        )

        st.subheader("Global Weather Map")
        map_df = df_f.dropna(subset=["latitude", "longitude"])
        if map_df.empty:
            st.info("No latitude/longitude available for the current filters.")
        else:
            fig = px.scatter_geo(
                map_df,
                lat="latitude",
                lon="longitude",
                color=metric,
                hover_name="country",
                hover_data={"location_name": True, "last_updated": True, metric: True},
                color_continuous_scale="Viridis",
                projection="natural earth",
                title=f"Global {metric_label}",
            )
            plot_block(fig)
            st.caption("Hover for details, use toolbar to zoom, pan or download PNG.")

# ---------------------------------------------------------------------
# Statistical Analysis
# ---------------------------------------------------------------------

elif page == "Statistical Analysis":
    if df_f.empty:
        st.info("No data for the selected filters. Try expanding the date range.")
    else:
        st.header("Statistical Analysis")

        st.subheader("Temperature vs Humidity")
        fig = px.scatter(
            df_f,
            x="temperature_celsius",
            y="humidity",
            color="country",
            hover_data=["location_name", "last_updated"],
            title="Temperature vs Humidity by Country",
        )
        plot_block(fig)
        st.caption("Use hover to inspect individual observations.")

        st.subheader("Country-wise Mean Metric")
        country_agg = df_f.groupby("country")[metric].mean().reset_index()
        fig = px.bar(
            country_agg,
            x="country",
            y=metric,
            title=f"Mean {metric_label} by Country",
        )
        plot_block(fig)

        st.subheader("Correlation Heatmap")
        corr_cols = [
            "temperature_celsius",
            "humidity",
            "precip_mm",
            "wind_kph",
            "heat_index",
            "wind_chill",
        ]
        corr = df_f[corr_cols].corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title="Correlation Between Weather Metrics",
        )
        plot_block(fig)

        st.subheader("Descriptive Statistics")
        st.dataframe(df_f[corr_cols].describe().T)

        # Density plot (KDE)
        st.subheader(f"Density of {metric_label}")
        fig = px.histogram(
            df_f,
            x=metric,
            color="country",
            histnorm="probability density",
            marginal="violin",
            nbins=40,
            opacity=0.6,
            title=f"Estimated Density of {metric_label}",
        )
        plot_block(fig)

        # Multi-metric country comparison
        st.subheader("Country Comparison Across Metrics")
        compare_metrics = ["temperature_celsius", "humidity", "precip_mm", "wind_kph"]
        country_stats = df_f.groupby("country")[compare_metrics].mean().reset_index()
        melted = country_stats.melt(
            id_vars="country", var_name="metric", value_name="value"
        )
        fig = px.bar(
            melted,
            x="country",
            y="value",
            color="metric",
            barmode="group",
            title="Mean Values by Country and Metric",
        )
        plot_block(fig)

# ---------------------------------------------------------------------
# Climate Trends
# ---------------------------------------------------------------------

elif page == "Climate Trends":
    if df_f.empty:
        st.info("No data for the selected filters. Try a date range that overlaps 2023.")
    else:
        st.header("Climate Trends")

        st.subheader(f"{metric_label} Over Time")
        ts = df_f.sort_values("last_updated")
        fig = px.line(
            ts,
            x="last_updated",
            y=metric_to_plot,
            color="country",
            title=f"{metric_label} Time Series",
        )
        fig.update_xaxes(rangeslider_visible=True)
        plot_block(fig)
        st.caption("Drag the range slider to zoom into specific periods.")

        # 7‑day moving average
        st.subheader(f"{metric_label} – 7‑Day Moving Average")
        ts_ma = ts.sort_values("last_updated").copy()
        ts_ma["rolling_mean"] = (
            ts_ma.groupby("country")[metric]
            .transform(lambda s: s.rolling(window=7, min_periods=3).mean())
        )
        fig = px.line(
            ts_ma,
            x="last_updated",
            y="rolling_mean",
            color="country",
            title=f"{metric_label} (7‑Day Moving Average)",
        )
        plot_block(fig)

        st.subheader("Area Chart")
        fig = px.area(
            ts,
            x="last_updated",
            y=metric_to_plot,
            color="country",
            title=f"{metric_label} Area Chart",
        )
        plot_block(fig)

        st.subheader("Distributions")
        c1, c2 = st.columns(2)

        with c1:
            fig = px.histogram(
                df_f,
                x=metric,
                color="country",
                nbins=30,
                marginal="box",
                title=f"Histogram of {metric_label}",
            )
            plot_block(fig)

        with c2:
            fig = px.violin(
                df_f,
                x="country",
                y=metric,
                box=True,
                points="all",
                title=f"Violin Plot of {metric_label} by Country",
            )
            plot_block(fig)

        fig = px.box(
            df_f,
            x="country",
            y=metric,
            title=f"Box Plot of {metric_label} by Country",
        )
        plot_block(fig)

        # Monthly aggregation line chart
        st.subheader(f"Monthly Average {metric_label}")
        monthly = (
            df_f.set_index("last_updated")
            .groupby([pd.Grouper(freq="M"), "country"])[metric]
            .mean()
            .reset_index()
        )
        monthly["month"] = monthly["last_updated"].dt.to_period("M").astype(str)
        fig = px.line(
            monthly,
            x="month",
            y=metric,
            color="country",
            markers=True,
            title=f"Monthly Mean {metric_label} by Country",
        )
        plot_block(fig)

        st.subheader("Monthly Heatmap")
        month_means = df_f.groupby(["country", "month"])[metric].mean().reset_index()
        fig = px.density_heatmap(
            month_means,
            x="month",
            y="country",
            z=metric,
            color_continuous_scale="Viridis",
            title=f"Monthly {metric_label} by Country",
        )
        plot_block(fig)

        st.subheader("Radar Chart of Mean Metrics")
        radar_metrics = ["temperature_celsius", "humidity", "precip_mm", "wind_kph"]
        radar_agg = df_f.groupby("country")[radar_metrics].mean().reset_index()
        if not radar_agg.empty:
            fig = go.Figure()
            for _, row in radar_agg.iterrows():
                fig.add_trace(
                    go.Scatterpolar(
                        r=row[radar_metrics].values,
                        theta=radar_metrics,
                        fill="toself",
                        name=row["country"],
                    )
                )
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True)),
                showlegend=True,
                title="Radar Chart of Average Conditions by Country",
            )
            plot_block(fig)

# ---------------------------------------------------------------------
# Extreme Events
# ---------------------------------------------------------------------

elif page == "Extreme Events":
    if df_f.empty:
        st.info("No data for the selected filters. Try a 2023 date range.")
    else:
        st.header("Extreme Events")

        extremes = df_f[df_f[metric] >= threshold].copy()

        st.subheader("Top Extremes")
        c1, c2 = st.columns(2)

        with c1:
            hottest = df_f.sort_values("temperature_celsius", ascending=False).head(5)
            st.write("Top 5 Hottest Records")
            st.dataframe(
                hottest[
                    ["country", "location_name", "last_updated", "temperature_celsius"]
                ]
            )

            rainiest = df_f.sort_values("precip_mm", ascending=False).head(5)
            st.write("Top 5 Highest Precipitation")
            st.dataframe(
                rainiest[["country", "location_name", "last_updated", "precip_mm"]]
            )

        with c2:
            coldest = df_f.sort_values("temperature_celsius", ascending=True).head(5)
            st.write("Top 5 Coldest Records")
            st.dataframe(
                coldest[
                    ["country", "location_name", "last_updated", "temperature_celsius"]
                ]
            )

            windiest = df_f.sort_values("wind_kph", ascending=False).head(5)
            st.write("Top 5 Highest Wind Speed")
            st.dataframe(
                windiest[["country", "location_name", "last_updated", "wind_kph"]]
            )

        if extremes.empty:
            st.info("No extreme events found with the current metric and threshold.")
        else:
            st.subheader("Extreme Events Frequency by Country")
            freq_country = (
                extremes["country"]
                .value_counts()
                .rename_axis("country")
                .reset_index(name="count")
            )
            fig = px.bar(
                freq_country,
                x="country",
                y="count",
                title=f"Number of {metric_label} Extreme Events by Country",
            )
            plot_block(fig)

            st.subheader("Monthly Extreme Events")
            monthly_counts = extremes.groupby("month").size().reset_index(name="count")
            fig = px.line(
                monthly_counts,
                x="month",
                y="count",
                markers=True,
                title=f"Monthly Count of {metric_label} Extreme Events",
            )
            plot_block(fig)

            st.subheader("Regional Extreme Events Table")
            st.dataframe(
                extremes[
                    ["country", "location_name", "last_updated", metric]
                ].sort_values(metric, ascending=False)
            )

            st.subheader("Extreme Events Map")
            geo_extreme = extremes.dropna(subset=["iso_code"])
            if geo_extreme.empty:
                st.info("No ISO‑3 codes available for a choropleth in the current selection.")
            else:
                mean_extreme = (
                    geo_extreme.groupby(["country", "iso_code"])[metric]
                    .mean()
                    .reset_index()
                )
                fig = px.choropleth(
                    mean_extreme,
                    locations="iso_code",
                    color=metric,
                    hover_name="country",
                    color_continuous_scale="Reds",
                    title=f"Average Extreme {metric_label} by Country",
                )
                plot_block(fig)

            # Bubble chart: intensity of extremes
            st.subheader("Extreme Events Bubble Chart")
            fig = px.scatter(
                extremes,
                x="temperature_celsius",
                y="humidity",
                size="wind_kph",
                color="country",
                hover_data=["location_name", "last_updated", metric],
                title="Temperature vs Humidity for Extreme Events (Bubble size = Wind speed)",
            )
            plot_block(fig)

            # Extreme type frequency (hot / cold / wet / windy)
            st.subheader("Extreme Events by Type")

            def label_extreme(row):
                tags = []
                if row["temperature_celsius"] >= df["temperature_celsius"].quantile(0.95):
                    tags.append("Hot")
                if row["temperature_celsius"] <= df["temperature_celsius"].quantile(0.05):
                    tags.append("Cold")
                if row["precip_mm"] >= df["precip_mm"].quantile(0.95):
                    tags.append("Wet")
                if row["wind_kph"] >= df["wind_kph"].quantile(0.95):
                    tags.append("Windy")
                return ",".join(tags) or "Other"

            extremes["extreme_type"] = extremes.apply(label_extreme, axis=1)
            type_counts = (
                extremes["extreme_type"]
                .value_counts()
                .rename_axis("extreme_type")
                .reset_index(name="count")
            )
            fig = px.bar(
                type_counts,
                x="extreme_type",
                y="count",
                title="Extreme Events by Category",
            )
            plot_block(fig)

# ---------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------

elif page == "Help":
    st.header("Help & User Guide")
    st.markdown(
        """
        **Using the filters**

        - Pick one or more countries from the sidebar.
        - Choose a date range (the dataset currently contains records from 2023).
        - Select the metric and a threshold if you care about extremes.

        **Pages**

        - *Executive Dashboard* – quick KPIs, latest snapshot, global map.
        - *Statistical Analysis* – scatter plots, density plot, country comparisons, correlations.
        - *Climate Trends* – raw and smoothed time series, distributions, monthly trends, radar chart.
        - *Extreme Events* – hottest/coldest days, rain and wind extremes, frequencies, bubble chart, maps.

        All charts support hover, zoom, pan, and PNG download using the Plotly toolbar.
        """
    )







