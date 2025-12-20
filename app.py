import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# CONFIG + THEME (Light mode, cyan + deep-blue accents)
# =====================================================
st.set_page_config(
    page_title="ClimateScope Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# CSS (light background, cyan/deep-blue accents)
# =====================================================
@st.cache_data(show_spinner=False)
@st.cache_data(show_spinner=False)
def load_css():
    return """
    <style>
    /* ===== COLOR VARIABLES ===== */
    :root{
        --main-cyan: #e0fbff;        /* main page cyan */
        --sidebar-deep: #0b3d91;     /* complementary deep blue */
        --card-white: #ffffff;
        --accent-cyan: #06b6d4;
        --text-dark: #0f172a;
        --text-light: #f8fafc;
    }

    /* ===== MAIN PAGE ===== */
    .stApp {
        background-color: var(--main-cyan);
        color: var(--text-dark);
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0b3d91 0%,
            #1e40af 100%
        );
        color: var(--text-light);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-light) !important;
    }

    /* ===== SIDEBAR INPUTS ===== */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] textarea {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        border-radius: 6px;
    }

    /* ===== KPI CARDS ===== */
    .kpi-box {
        background: var(--card-white);
        border-left: 5px solid var(--accent-cyan);
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    .kpi-value {
        color: #0b3d91;
        font-weight: 700;
    }

    /* ===== INSIGHT CARDS ===== */
    .insight-card {
        background: var(--card-white);
        border-left: 6px solid var(--accent-cyan);
        border-radius: 10px;
        padding: 14px;
    }

    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        background: var(--card-white);
        border-radius: 10px;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton button {
        background: linear-gradient(90deg, #06b6d4, #0b3d91) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
    """

st.markdown(load_css(), unsafe_allow_html=True)


# =====================================================
# DATA PATH (user provided)
# =====================================================
DATA_PATH = r"C:\Users\harsh\PycharmProjects\ClimateScope1\Climate-Scope-PROJECT\GlobalWeatherRepository_cleaned.csv"

# =====================================================
# UTILITIES
# =====================================================
def kpi_class(val, low, mid):
    return "kpi-good" if val <= low else "kpi-warning" if val <= mid else "kpi-critical"

@st.cache_data(show_spinner=False)
def load_data(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=["last_updated"])
    df["date"] = df["last_updated"].dt.normalize()
    df["month"] = df["last_updated"].dt.month
    df["month_name"] = df["last_updated"].dt.strftime("%b")

    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn"
    }
    df["season"] = df["month"].apply(lambda m: season_map.get(m))
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
# SIDEBAR — FILTERS FIRST, THEN OPTIONS (reordered as requested)
# =====================================================
st.sidebar.markdown("# 🎯 Filter Data")
st.sidebar.markdown("---")

# Filters block (appear first)
countries = st.sidebar.multiselect("🌐 Select Countries", sorted(df["country"].unique()))
date_range = st.sidebar.date_input("📅 Date Range", [df["date"].min(), df["date"].max()])

metric = st.sidebar.selectbox(
    "📈 Climate Metric",
    ["temperature_celsius","humidity","precip_mm","wind_kph","heat_index","wind_chill","temp_7day_avg"],
    format_func=lambda x: x.replace("_"," ").title()
)

aggregation = st.sidebar.selectbox("⏱ Time Aggregation", ["Daily","Monthly","Seasonal"])
normalize = st.sidebar.checkbox("🔢 Normalize Metric (0–1)")
threshold = st.sidebar.number_input("🔥 Extreme Event Threshold", value=35.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.markdown("# ⚙️ Options")
# Options block (page choice after filters)
page = st.sidebar.radio(
    "📊 Navigate Dashboard",
    ["Executive Dashboard","Statistical Analysis","Climate Trends","Extreme Events","Help"]
)
st.sidebar.markdown("---")

# =====================================================
# DATA FILTERING
# =====================================================
@st.cache_data(show_spinner=False)
def filter_data(df, selected_countries, start, end, metric_col, do_normalize):
    d = df.copy()
    if selected_countries:
        d = d[d["country"].isin(selected_countries)]
    d = d[(d["date"] >= pd.to_datetime(start)) & (d["date"] <= pd.to_datetime(end))]
    if do_normalize and (metric_col in d.columns):
        mn = d[metric_col].min()
        mx = d[metric_col].max()
        if mx != mn:
            d[metric_col] = (d[metric_col] - mn) / (mx - mn)
    return d

filtered = filter_data(df, tuple(countries), date_range[0], date_range[1], metric, normalize)

# =====================================================
# PLOTLY TEMPLATE (light mode, cyan/deep-blue palette)
# =====================================================
def get_plotly_template():
    return dict(
        layout=dict(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f5fbff",
            font=dict(family="Inter, system-ui, sans-serif", color="#0b3d91"),
            title=dict(font=dict(size=18, family="Inter", color="#0b3d91"), x=0.5),
            xaxis=dict(gridcolor='rgba(11,61,145,0.06)', zerolinecolor='rgba(11,61,145,0.08)'),
            yaxis=dict(gridcolor='rgba(11,61,145,0.06)', zerolinecolor='rgba(11,61,145,0.08)'),
            legend=dict(bgcolor='rgba(240,248,255,0.6)', bordercolor='rgba(11,61,145,0.06)', borderwidth=1),
            colorway=['#06b6d4','#0b3d91','#22c1c3','#1e40af','#0891b2','#0ea5a4']
        )
    )

# =====================================================
# KPI VALUES & SECTION
# =====================================================
st.markdown("## 📊 Climate Performance Indicators")
st.markdown("---")
col1, col2, col3 = st.columns(3)

avg_temp = round(filtered["temperature_celsius"].mean(), 1) if len(filtered) else 0
rain_mean = filtered["precip_mm"].mean() if len(filtered) else 0
rain_var = round((filtered["precip_mm"].std() / rain_mean) * 100, 1) if rain_mean > 0 else 0

total_rows = len(filtered)
extreme_hits = (filtered["temperature_celsius"] > threshold).sum() if "temperature_celsius" in filtered.columns else 0
extreme_score = round((extreme_hits / total_rows) * 100, 1) if total_rows else 0

with col1:
    trend = "↑ +2.3%" if avg_temp > 24 else "↓ -1.5%"
    trend_class = "positive" if avg_temp <= 24 else "negative"
    st.markdown(f"""
    <div class="kpi-box {kpi_class(avg_temp, 22, 28)}">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="kpi-icon">🌡</div>
                <div class="kpi-label">Average Temperature</div>
                <div class="kpi-value">{avg_temp}°C</div>
            </div>
            <div style="text-align:right;color:var(--muted);font-size:12px;">{trend}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    tr = "↑ +5.1%" if rain_var > 15 else "→ Stable"
    st.markdown(f"""
    <div class="kpi-box {kpi_class(rain_var, 10, 20)}">
        <div>
            <div class="kpi-icon">🌧</div>
            <div class="kpi-label">Rainfall Variability</div>
            <div class="kpi-value">{rain_var}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    tr2 = "↑ High Risk" if extreme_score > 70 else "↓ Moderate"
    st.markdown(f"""
    <div class="kpi-box {kpi_class(extreme_score, 40, 70)}">
        <div>
            <div class="kpi-icon">🔥</div>
            <div class="kpi-label">Extreme Event Risk</div>
            <div class="kpi-value">{extreme_score}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# INSIGHTS
# =====================================================
st.markdown("## 🧠 Climate Intelligence Insights")
st.markdown("---")
if avg_temp > 28:
    insight_class = "insight-critical"
    insight = "🌡 *Critical Temperature Alert* — Immediate action required."
elif avg_temp > 24:
    insight_class = "insight-warning"
    insight = "⚠ *Rising Temperature Trend* — Monitor closely."
else:
    insight_class = "insight-positive"
    insight = "✅ *Temperature Stability Maintained*."

st.markdown(f"""
<div class="insight-card {insight_class}">
    <strong>{insight}</strong><br><br>
    🔍 Rainfall variability: <strong>{rain_var}%</strong> • Extreme event probability: <strong>{extreme_score}%</strong>.
</div>
""", unsafe_allow_html=True)

# =====================================================
# PAGE: Executive Dashboard
# =====================================================
if page == "Executive Dashboard":
    st.title("🌍 Executive Climate Overview")
    st.markdown("Real-time climate intelligence for strategic decision-making")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    def get_color_scale(m):
        if m in ["temperature_celsius", "heat_index"]:
            return "RdYlBu"
        elif m in ["humidity", "precip_mm"]:
            return "Blues"
        elif m in ["wind_kph", "wind_chill"]:
            return "Viridis"
        else:
            return "Teal"

    color_scale = get_color_scale(metric)

    @st.cache_data(show_spinner=False)
    def prepare_map_data(df_local, metric_local):
        cols = ["latitude", "longitude", "location_name", "country", "date", metric_local]
        d = df_local[cols].dropna(subset=["latitude", "longitude", metric_local])
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
        marker=dict(size=9, opacity=0.85, line=dict(width=0.4, color="rgba(11,61,145,0.12)"))
    )
    fig_scatter.update_layout(
        **get_plotly_template()['layout'],
        geo=dict(
            showland=True,
            landcolor="#ffffff",
            showcountries=True,
            countrycolor="rgba(11,61,145,0.12)",
            showocean=True,
            oceancolor="#f0f9ff",
            coastlinecolor="rgba(11,61,145,0.12)"
        ),
        margin=dict(l=0, r=0, t=60, b=0)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption(f"🔍 City-level {metric_label} distribution reveals geographic patterns.")

    st.markdown("---")

    @st.cache_data(show_spinner=False)
    def compute_country_avg(df_local, metric_local):
        return df_local[["country", metric_local]].groupby("country", as_index=False)[metric_local].mean()

    country_avg = compute_country_avg(filtered, metric)

    fig_choro = px.choropleth(
        country_avg,
        locations="country",
        locationmode="country names",
        color=metric,
        color_continuous_scale=color_scale,
        hover_name="country",
        labels={metric: metric_label},
        title=f"🗺 Country-Level Average: {metric_label}"
    )
    fig_choro.update_layout(
        **get_plotly_template()['layout'],
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="rgba(11,61,145,0.12)"),
        margin=dict(l=0, r=0, t=60, b=0)
    )
    st.plotly_chart(fig_choro, use_container_width=True)
    st.caption(f"🔍 National {metric_label} averages highlight macro trends.")

    st.download_button(
        label="📥 Download Executive Data (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="climatescope_executive_dashboard.csv",
        mime="text/csv"
    )

# =====================================================
# PAGE: Statistical Analysis
# =====================================================
elif page == "Statistical Analysis":
    st.title("📊 Statistical Climate Analysis")
    st.markdown("Advanced analytics and correlation insights")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    # SCATTER PLOT (no trendline)
    st.subheader("🔗 Temperature vs Humidity Correlation")
    scatter_df = filtered[["temperature_celsius", "humidity", "country"]].dropna()

    fig_scatter = px.scatter(
        scatter_df,
        x="temperature_celsius",
        y="humidity",
        color="country",
        opacity=0.7,
        title="Climate Correlation: Temperature vs Humidity",
        labels={"temperature_celsius": "Temperature (°C)", "humidity": "Humidity (%)"}
    )
    fig_scatter.update_traces(marker=dict(size=8, line=dict(width=0.4, color="rgba(11,61,145,0.06)")))
    fig_scatter.update_layout(**get_plotly_template()['layout'])
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("🔍 Correlation patterns reveal interdependencies.")

    # BAR CHART
    st.subheader(f"📊 Top 15 Countries by {metric_label}")
    @st.cache_data(show_spinner=False)
    def compute_country_avg_bar(df_local, metric_local):
        return df_local[["country", metric_local]].groupby("country", as_index=False)[metric_local].mean().sort_values(metric_local, ascending=False).head(15)

    country_avg_bar = compute_country_avg_bar(filtered, metric)

    fig_bar = px.bar(
        country_avg_bar,
        x="country",
        y=metric,
        color=metric,
        color_continuous_scale="Teal",
        title=f"{metric_label} by Country",
        labels={"country": "Country", metric: metric_label}
    )
    fig_bar.update_layout(**get_plotly_template()['layout'])
    fig_bar.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption(f"🔍 Top countries show {metric_label} dominance.")

    # HISTOGRAM
    st.subheader(f"📈 Distribution Analysis: {metric_label}")
    fig_hist = px.histogram(
        filtered.dropna(subset=[metric]),
        x=metric,
        nbins=50,
        marginal="box",
        title=f"Frequency Distribution: {metric_label}",
        labels={metric: metric_label}
    )
    fig_hist.update_layout(**get_plotly_template()['layout'])
    st.plotly_chart(fig_hist, use_container_width=True)
    st.caption("🔍 Distribution curve shows concentration and outliers.")

    # BOX PLOT
    st.subheader(f"📦 Variability Analysis: {metric_label}")
    fig_box = px.box(
        filtered.dropna(subset=[metric]),
        x="country",
        y=metric,
        color="country",
        title=f"Statistical Spread: {metric_label} by Country",
        labels={"country": "Country", metric: metric_label}
    )
    fig_box.update_layout(**get_plotly_template()['layout'], showlegend=False)
    fig_box.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption("🔍 Box plots reveal range and outliers.")

    # CORRELATION HEATMAP
    st.subheader("🔥 Climate Metrics Correlation Matrix")
    @st.cache_data(show_spinner=False)
    def compute_correlation(df_local):
        return df_local[["temperature_celsius", "humidity", "precip_mm", "wind_kph"]].corr()

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
    st.caption("🔍 Heatmap quantifies relationships (-1 to +1).")

    st.subheader("📋 Statistical Summary")
    st.dataframe(filtered.describe(), use_container_width=True)

    st.download_button(
        "📥 Download Statistical Data",
        filtered.to_csv(index=False).encode("utf-8"),
        "climatescope_statistical_analysis.csv",
        mime="text/csv"
    )

# =====================================================
# PAGE: Climate Trends
# =====================================================
elif page == "Climate Trends":
    st.title("📈 Climate Trends Analysis")
    st.markdown("Temporal patterns and seasonal intelligence")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()
    max_date = filtered["date"].max() if not filtered.empty else pd.Timestamp.now()

    st.subheader(f"📊 Temporal Evolution: {metric_label}")
    fig = px.line(
        filtered,
        x="date",
        y=metric,
        color="country",
        markers=True,
        title=f"Time Series: {metric_label}",
        labels={"date": "Date", metric: metric_label, "country": "Country"}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    fig.update_traces(line=dict(width=2.2), marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 Trend lines reveal long-term patterns.")

    st.download_button(
        "📥 Download Trend Data",
        filtered[["date", "country", metric]].to_csv(index=False).encode("utf-8"),
        "trend_over_time.csv",
        mime="text/csv"
    )

    st.subheader("🔄 Historical vs Recent Comparison")
    @st.cache_data(show_spinner=False)
    def compute_avg_recent(df_local, metric_local, reference_date):
        d = df_local[["date", "country", metric_local]].dropna()
        d = d.assign(period=np.where(d["date"] >= reference_date - pd.Timedelta(days=30), "Last 30 Days", "Historical Average"))
        return d.groupby(["period", "country"], sort=False)[metric_local].mean().reset_index()

    avg_recent = compute_avg_recent(filtered, metric, max_date)

    fig = px.bar(
        avg_recent,
        x="country",
        y=metric,
        color="period",
        barmode="group",
        title=f"Comparative Period Analysis: {metric_label}",
        labels={"country": "Country", metric: metric_label, "period": "Time Period"},
        color_discrete_map={"Last 30 Days": "#06b6d4", "Historical Average": "#0b3d91"}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 Recent vs historical baselines.")

    st.download_button(
        "📥 Download Comparison Data",
        avg_recent.to_csv(index=False).encode("utf-8"),
        "trend_avg_vs_recent.csv",
        mime="text/csv"
    )

    st.subheader("🍂 Seasonal Climate Patterns")
    @st.cache_data(show_spinner=False)
    def compute_seasonal_avg(df_local, metric_local):
        return df_local[["season","country",metric_local]].groupby(["season","country"], sort=False)[metric_local].mean().reset_index()

    seasonal_avg = compute_seasonal_avg(filtered, metric)

    fig = px.bar(
        seasonal_avg,
        x="season",
        y=metric,
        color="country",
        barmode="group",
        title=f"Seasonal Climate Analysis: {metric_label}",
        labels={"season":"Season", metric: metric_label, "country":"Country"},
        category_orders={"season":["Winter","Spring","Summer","Autumn"]}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 Seasonal variations expose cycles.")

    st.download_button(
        "📥 Download Seasonal Data",
        seasonal_avg.to_csv(index=False).encode("utf-8"),
        "trend_seasonal.csv",
        mime="text/csv"
    )

    st.subheader("🌍 Geographic Climate Distribution")
    @st.cache_data(show_spinner=False)
    def compute_country_avg_simple(df_local, metric_local):
        return df_local[["country",metric_local]].groupby("country", sort=False)[metric_local].mean().reset_index()

    country_avg_simple = compute_country_avg_simple(filtered, metric)
    fig = px.bar(
        country_avg_simple,
        x="country",
        y=metric,
        color=metric,
        color_continuous_scale="Viridis",
        title=f"Country-Level Baseline: {metric_label}",
        labels={"country":"Country", metric:metric_label}
    )
    fig.update_layout(**get_plotly_template()['layout'])
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔍 Geographic averages establish baselines.")

    st.download_button(
        "📥 Download Country Averages",
        country_avg_simple.to_csv(index=False).encode("utf-8"),
        "trend_country_avg.csv",
        mime="text/csv"
    )

# =====================================================
# PAGE: Extreme Events
# =====================================================
elif page == "Extreme Events":
    st.title("🔥 Extreme Climate Events Analysis")
    st.markdown("Critical event detection and risk assessment")
    st.markdown("---")

    metric_label = metric.replace("_", " ").title()

    @st.cache_data(show_spinner=False)
    def get_extreme_events(df_local, metric_local, threshold_local):
        cols = ["date","country","location_name","season","latitude","longitude",metric_local]
        d = df_local[cols].dropna(subset=[metric_local])
        return d[d[metric_local] >= threshold_local]

    extreme = get_extreme_events(filtered, metric, threshold)

    if extreme.empty:
        st.markdown('<div class="extreme-banner">⚠ No Extreme Events Detected for the chosen filters and threshold.</div>', unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        total_events = len(extreme)
        max_value = extreme[metric].max()
        top_country = extreme["country"].mode()[0] if not extreme["country"].mode().empty else "N/A"

        c1.metric("🚨 Total Extreme Events", f"{total_events:,}")
        c2.metric("📊 Peak Value Recorded", f"{max_value:.2f}")
        c3.metric("🌍 Most Affected Region", top_country)

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("📅 Extreme Events Timeline")
        time_fig = px.scatter(
            extreme,
            x="date",
            y=metric,
            color="country",
            size=metric,
            hover_data=["location_name","season"],
            title=f"Chronological Extreme Event Distribution: {metric_label}",
            labels={"date":"Date", metric:metric_label, "country":"Country"}
        )
        layout_settings = get_plotly_template()['layout'].copy()
        layout_settings.update({
            'plot_bgcolor': '#f0fbff',
            'paper_bgcolor': '#ffffff',
            'title': dict(font=dict(size=16, color='#0b3d91'), x=0.5)
        })
        time_fig.update_layout(**layout_settings)
        time_fig.update_traces(marker=dict(line=dict(width=0.6, color='rgba(11,61,145,0.12)'), opacity=0.85))
        st.plotly_chart(time_fig, use_container_width=True)
        st.caption("🔍 Event timeline shows temporal clustering.")

        st.download_button(
            "📥 Download Timeline Data",
            extreme[["date","country",metric]].to_csv(index=False).encode("utf-8"),
            "extreme_timeline.csv",
            mime="text/csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("🗺 Geographic Hotspot Analysis")
        map_fig = px.scatter_geo(
            extreme,
            lat="latitude",
            lon="longitude",
            color=metric,
            size=metric,
            color_continuous_scale="Reds",
            hover_name="location_name",
            hover_data=["country","season"],
            projection="natural earth",
            title=f"Extreme Event Geographic Distribution: {metric_label}",
            labels={metric:metric_label}
        )
        layout_settings = get_plotly_template()['layout'].copy()
        layout_settings.update({
            'geo': dict(showland=True, landcolor="#ffffff", showcountries=True, countrycolor="rgba(11,61,145,0.12)", showocean=True, oceancolor="#f0fbff"),
            'title': dict(font=dict(size=16, color='#0b3d91'), x=0.5)
        })
        map_fig.update_layout(**layout_settings)
        st.plotly_chart(map_fig, use_container_width=True)
        st.caption("🔍 Geographic clustering reveals high-risk zones.")

        st.download_button(
            "📥 Download Location Data",
            extreme.to_csv(index=False).encode("utf-8"),
            "extreme_locations.csv",
            mime="text/csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("🍂 Seasonal Extreme Event Distribution")
        seasonal = extreme.groupby(["season","country"]).size().reset_index(name="event_count")
        fig = px.bar(
            seasonal,
            x="season",
            y="event_count",
            color="country",
            barmode="group",
            title="Seasonal Frequency Analysis: Extreme Events",
            labels={"season":"Season","event_count":"Number of Events","country":"Country"},
            category_orders={"season":["Winter","Spring","Summer","Autumn"]}
        )
        ls = get_plotly_template()['layout'].copy()
        ls.update({'title': dict(font=dict(size=16, color='#0b3d91'), x=0.5)})
        fig.update_layout(**ls)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🔍 Seasonal patterns reveal vulnerability windows.")

        st.download_button(
            "📥 Download Seasonal Data",
            seasonal.to_csv(index=False).encode("utf-8"),
            "extreme_seasonal.csv",
            mime="text/csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Complete Extreme Events Database")
        st.dataframe(extreme.sort_values(metric, ascending=False), use_container_width=True)

        st.download_button(
            "📥 Download All Events",
            extreme.to_csv(index=False).encode("utf-8"),
            "all_extreme_events.csv",
            mime="text/csv"
        )

# =====================================================
# PAGE: HELP
# =====================================================
else:
    st.title("❓ ClimateScope User Guide")
    st.markdown("Your comprehensive guide to climate intelligence")
    st.markdown("---")

    st.markdown("""
    ### 🌍 About ClimateScope
    ClimateScope is a climate analytics platform for researchers, policy makers, and organizations.

    ### 🎯 Key Features
    - Executive Dashboard: global mapping, KPIs, download
    - Statistical Analysis: correlation, distribution, heatmap
    - Climate Trends: time series, seasonal, comparisons
    - Extreme Events: threshold detection, timeline, hotspots

    ### 🛠 How to Use
    1. Configure Filters (left): choose countries, dates, metric, normalization, threshold.
    2. Use Options below Filters to navigate pages.
    3. Hover charts, download CSVs for reports.

    ### 📥 Export Current Dataset
    """)

    st.download_button(
        label="📥 Download Filtered Climate Data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="ClimateScope_Filtered_Data.csv",
        mime="text/csv"
    )
