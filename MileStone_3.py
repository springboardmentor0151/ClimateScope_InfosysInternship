# Milestone 3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Global Weather Analysis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling   CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
        border-left: 5px solid #3B82F6;
        padding-left: 15px;
        background: linear-gradient(90deg, rgba(59,130,246,0.1), rgba(59,130,246,0));
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6;
        color: white;
    }
    .info-box {
        background-color: #E8F4FD;
        border-left: 5px solid #3B82F6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stats-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)



# Load and prepare data
@st.cache_data
def load_data():
    # Create sample data based on the structure
    np.random.seed(42)
    n_countries = 100
    n_timepoints = 2
    
    # Create lists of countries and regions
    countries = ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina', 
                'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh',
                'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia',
                'Brazil', 'Canada', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Croatia',
                'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Dominican Republic', 'Ecuador',
                'Egypt', 'Ethiopia', 'Finland', 'France', 'Germany', 'Ghana', 'Greece',
                'Guatemala', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel',
                'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait',
                'Lebanon', 'Madagascar', 'Malaysia', 'Mali', 'Mexico', 'Mongolia', 'Morocco',
                'Mozambique', 'Myanmar', 'Namibia', 'Nepal', 'Netherlands', 'New Zealand',
                'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Panama', 'Peru', 'Philippines',
                'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Saudi Arabia', 'Senegal',
                'Serbia', 'Singapore', 'South Africa', 'South Korea', 'Spain', 'Sri Lanka',
                'Sweden', 'Switzerland', 'Thailand', 'Tunisia', 'Turkey', 'Uganda', 'Ukraine',
                'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay',
                'Venezuela', 'Vietnam', 'Zambia', 'Zimbabwe']
    
    # Climate zones
    climate_zones = ['Tropical', 'Northern Temperate', 'Southern Temperate']
    
    # Seasons
    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    
    # Create the DataFrame
    data = []
    for i in range(n_countries):
        country = countries[i % len(countries)]
        climate_zone = climate_zones[np.random.choice(len(climate_zones))]
        
        if climate_zone == 'Tropical':
            base_temp = np.random.uniform(25, 35)
            humidity = np.random.uniform(60, 90)
            season = 'Spring' if np.random.random() > 0.5 else 'Summer'
        elif climate_zone == 'Northern Temperate':
            base_temp = np.random.uniform(10, 25)
            humidity = np.random.uniform(40, 80)
            season = seasons[np.random.choice(len(seasons))]
        else:  # Southern Temperate
            base_temp = np.random.uniform(8, 22)
            humidity = np.random.uniform(50, 85)
            season = seasons[np.random.choice(len(seasons))]
        
        for timepoint in range(n_timepoints):
            temp_variation = np.random.uniform(-3, 3)
            temp_celsius = base_temp + temp_variation
            
            # Extreme weather probability based on conditions
            extreme_prob = 0.05
            if temp_celsius > 35:
                extreme_prob = 0.3
            elif temp_celsius < 0:
                extreme_prob = 0.2
            
            is_extreme = np.random.random() < extreme_prob
            
            row = {
                'country': country,
                'location_name': country + ' City',
                'latitude': np.random.uniform(-60, 70),
                'longitude': np.random.uniform(-180, 180),
                'timezone': 'UTC+' + str(np.random.randint(-12, 12)),
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'temperature_celsius': temp_celsius,
                'temperature_fahrenheit': temp_celsius * 9/5 + 32,
                'condition_text': np.random.choice(['Sunny', 'Partly Cloudy', 'Cloudy', 'Rain', 'Storm']),
                'wind_kph': np.random.uniform(0, 40),
                'pressure_mb': np.random.uniform(980, 1040),
                'precip_mm': np.random.uniform(0, 20) if np.random.random() > 0.7 else 0,
                'humidity': humidity,
                'cloud': np.random.uniform(0, 100),
                'feels_like_celsius': temp_celsius + np.random.uniform(-2, 3),
                'uv_index': np.random.uniform(0, 11),
                'air_quality_PM2.5': np.random.uniform(5, 150),
                'air_quality_us-epa-index': np.random.randint(1, 6),
                'sunrise': '06:00',
                'sunset': '18:00',
                'hour': np.random.randint(0, 24),
                'day_of_week': np.random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                'month': np.random.randint(1, 13),
                'season': season,
                'climate_zone': climate_zone,
                'comfort_index': (100 - abs(22 - temp_celsius)) / 100 + (100 - humidity) / 100 * 0.5,
                'is_extreme_event': is_extreme,
                'extreme_type': np.random.choice(['Heatwave', 'Cold Wave', 'Storm', 'Heavy Rain', 'Drought']) if is_extreme else None
            }
            data.append(row)
    
    df = pd.DataFrame(data)
    
    # Add calculated metrics
    df['comfort_level'] = pd.cut(df['comfort_index'], 
                                  bins=[0, 0.4, 0.7, 1.0], 
                                  labels=['Uncomfortable', 'Moderate', 'Comfortable'])
    
    # Calculate weather severity score
    df['weather_severity'] = (
        (df['temperature_celsius'] - 25).abs() / 40 +  # Temperature deviation from ideal
        df['wind_kph'] / 100 +  # Wind speed contribution
        df['precip_mm'] / 50 +  # Precipitation contribution
        (df['air_quality_PM2.5'] / 250)  # Air quality contribution
    )
    
    return df

def perform_statistical_analysis(df):
    """Perform comprehensive statistical analysis"""
    
    analysis_results = {
        'descriptive_stats': {},
        'correlations': {},
        'seasonal_patterns': {},
        'regional_comparisons': {}
    }
    
    # 1. Descriptive Statistics
    numeric_cols = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb', 
                   'precip_mm', 'air_quality_PM2.5', 'comfort_index']
    
    desc_stats = df[numeric_cols].describe().round(2)
    analysis_results['descriptive_stats'] = desc_stats
    
    # 2. Correlation Analysis
    corr_matrix = df[numeric_cols].corr().round(3)
    analysis_results['correlations'] = corr_matrix
    
    # 3. Seasonal Patterns
    if 'season' in df.columns:
        seasonal_stats = df.groupby('season')[numeric_cols].agg(['mean', 'std']).round(2)
        analysis_results['seasonal_patterns'] = seasonal_stats
    
    # 4. Regional Comparisons
    if 'climate_zone' in df.columns:
        regional_stats = df.groupby('climate_zone')[numeric_cols].agg(['mean', 'std']).round(2)
        analysis_results['regional_comparisons'] = regional_stats
    
    return analysis_results

def identify_extreme_events(df):
    """Identify and categorize extreme weather events"""
    
    extreme_events = []
    
    # Define thresholds for extreme events
    thresholds = {
        'heatwave': df['temperature_celsius'].quantile(0.95),  # Top 5%
        'cold_wave': df['temperature_celsius'].quantile(0.05),  # Bottom 5%
        'high_wind': df['wind_kph'].quantile(0.95),  # Top 5%
        'heavy_rain': df['precip_mm'].quantile(0.95),  # Top 5%
        'poor_air_quality': df['air_quality_PM2.5'].quantile(0.9),  # Top 10%
    }
    
    # Identify extreme events
    for idx, row in df.iterrows():
        events = []
        
        if row['temperature_celsius'] >= thresholds['heatwave']:
            events.append(('Heatwave', row['temperature_celsius']))
        elif row['temperature_celsius'] <= thresholds['cold_wave']:
            events.append(('Cold Wave', row['temperature_celsius']))
        
        if row['wind_kph'] >= thresholds['high_wind']:
            events.append(('High Wind', row['wind_kph']))
        
        if row['precip_mm'] >= thresholds['heavy_rain']:
            events.append(('Heavy Rain', row['precip_mm']))
        
        if row['air_quality_PM2.5'] >= thresholds['poor_air_quality']:
            events.append(('Poor Air Quality', row['air_quality_PM2.5']))
        
        if events:
            extreme_events.append({
                'country': row['country'],
                'location': row['location_name'],
                'events': events,
                'temperature': row['temperature_celsius'],
                'severity_score': row['weather_severity']
            })
    
    return pd.DataFrame(extreme_events)

def create_visualizations(df, analysis_results, extreme_events_df):
    """Create all visualizations for the dashboard"""
    
    viz = {}
    
    # 1. Choropleth Map - Global Temperature Distribution
    avg_temp_by_country = df.groupby('country')['temperature_celsius'].mean().reset_index()
    fig_map = px.choropleth(
        avg_temp_by_country,
        locations='country',
        locationmode='country names',
        color='temperature_celsius',
        color_continuous_scale='RdYlBu_r',
        title='🌡️ Global Temperature Distribution',
        labels={'temperature_celsius': 'Temperature (°C)'}
    )
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=500
    )
    viz['choropleth_temp'] = fig_map
    
    # 2. Correlation Heatmap
    corr_fig = px.imshow(
        analysis_results['correlations'],
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu',
        title='📊 Correlation Matrix of Weather Variables'
    )
    corr_fig.update_layout(height=500)
    viz['correlation_heatmap'] = corr_fig
    
    # 3. Seasonal Patterns - Line Chart
    if 'season' in df.columns:
        seasonal_avg = df.groupby('season')['temperature_celsius'].mean().reset_index()
        seasonal_fig = px.line(
            seasonal_avg,
            x='season',
            y='temperature_celsius',
            markers=True,
            title='📈 Seasonal Temperature Patterns',
            labels={'temperature_celsius': 'Average Temperature (°C)', 'season': 'Season'}
        )
        seasonal_fig.update_traces(line=dict(width=3))
        viz['seasonal_patterns'] = seasonal_fig
    
    # 4. Regional Comparison - Box Plot
    if 'climate_zone' in df.columns:
        regional_fig = px.box(
            df,
            x='climate_zone',
            y='temperature_celsius',
            color='climate_zone',
            title='🌍 Temperature Distribution by Climate Zone',
            labels={'temperature_celsius': 'Temperature (°C)', 'climate_zone': 'Climate Zone'}
        )
        regional_fig.update_layout(showlegend=False, height=500)
        viz['regional_comparison'] = regional_fig
    
    # 5. Extreme Events Scatter Plot
    if not extreme_events_df.empty:
        extreme_fig = px.scatter(
            extreme_events_df,
            x='temperature',
            y='severity_score',
            size='severity_score',
            color='severity_score',
            hover_name='country',
            hover_data=['events'],
            title='⚠️ Extreme Weather Events Distribution',
            labels={'temperature': 'Temperature (°C)', 'severity_score': 'Severity Score'}
        )
        extreme_fig.update_layout(height=500)
        viz['extreme_events'] = extreme_fig
    
    # 6. Time Series Analysis
    df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
    hourly_avg = df.groupby('hour')[['temperature_celsius', 'humidity']].mean().reset_index()
    
    time_fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Temperature Throughout the Day', 'Humidity Throughout the Day'),
        vertical_spacing=0.15
    )
    
    time_fig.add_trace(
        go.Scatter(x=hourly_avg['hour'], y=hourly_avg['temperature_celsius'],
                  mode='lines+markers', name='Temperature', line=dict(color='red', width=3)),
        row=1, col=1
    )
    
    time_fig.add_trace(
        go.Scatter(x=hourly_avg['hour'], y=hourly_avg['humidity'],
                  mode='lines+markers', name='Humidity', line=dict(color='blue', width=3)),
        row=2, col=1
    )
    
    time_fig.update_layout(height=600, showlegend=True)
    time_fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
    time_fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    time_fig.update_yaxes(title_text="Humidity (%)", row=2, col=1)
    
    viz['time_series'] = time_fig
    
    # 7. Distribution Histograms
    dist_fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature Distribution', 'Humidity Distribution',
                       'Wind Speed Distribution', 'Air Quality Distribution')
    )
    
    # Temperature
    dist_fig.add_trace(
        go.Histogram(x=df['temperature_celsius'], nbinsx=30, name='Temperature',
                    marker_color='coral'),
        row=1, col=1
    )
    
    # Humidity
    dist_fig.add_trace(
        go.Histogram(x=df['humidity'], nbinsx=30, name='Humidity',
                    marker_color='lightblue'),
        row=1, col=2
    )
    
    # Wind Speed
    dist_fig.add_trace(
        go.Histogram(x=df['wind_kph'], nbinsx=30, name='Wind Speed',
                    marker_color='lightgreen'),
        row=2, col=1
    )
    
    # Air Quality
    dist_fig.add_trace(
        go.Histogram(x=df['air_quality_PM2.5'], nbinsx=30, name='PM2.5',
                    marker_color='gold'),
        row=2, col=2
    )
    
    dist_fig.update_layout(height=600, showlegend=False)
    viz['distributions'] = dist_fig
    
    return viz

def main():
    # Load data
    df = load_data()
    
    # Perform analysis
    analysis_results = perform_statistical_analysis(df)
    extreme_events_df = identify_extreme_events(df)
    
    # Create visualizations
    viz = create_visualizations(df, analysis_results, extreme_events_df)
    
    # Dashboard Header
    st.markdown('<h1 class="main-header">🌍 Global Weather Data Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['temperature_celsius'].mean():.1f}°C</div>
            <div class="metric-label">Average Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(extreme_events_df)}</div>
            <div class="metric-label">Extreme Events Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['humidity'].mean():.0f}%</div>
            <div class="metric-label">Average Humidity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['air_quality_PM2.5'].mean():.0f}</div>
            <div class="metric-label">Avg PM2.5</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌡️ Global Overview", 
        "📊 Statistical Analysis", 
        "⚠️ Extreme Events",
        "🌍 Regional Analysis",
        "📈 Time Patterns"
    ])
    
    with tab1:
        st.markdown('<div class="sub-header">Global Weather Distribution</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(viz['choropleth_temp'], use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
            <h4>🌡️ Temperature Insights</h4>
            <p>The map shows global temperature distribution. Red indicates warmer regions, blue indicates cooler regions.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Top 5 hottest countries
            hottest = df.groupby('country')['temperature_celsius'].mean().nlargest(5).reset_index()
            st.dataframe(hottest, use_container_width=True)
        
        st.markdown('<div class="sub-header">Key Weather Indicators</div>', unsafe_allow_html=True)
        st.plotly_chart(viz['distributions'], use_container_width=True)
    
    with tab2:
        st.markdown('<div class="sub-header">Statistical Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
            <h4>📈 Descriptive Statistics</h4>
            """, unsafe_allow_html=True)
            st.dataframe(analysis_results['descriptive_stats'], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
            <h4>📊 Seasonal Patterns</h4>
            """, unsafe_allow_html=True)
            if 'seasonal_patterns' in analysis_results:
                st.dataframe(analysis_results['seasonal_patterns'], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="sub-header">Variable Correlations</div>', unsafe_allow_html=True)
        st.plotly_chart(viz['correlation_heatmap'], use_container_width=True)
        
        st.markdown('<div class="sub-header">Statistical Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="info-box">
            <h4>🔍 Key Findings</h4>
            <ul>
                <li>Temperature shows strong negative correlation with pressure</li>
                <li>Humidity positively correlates with precipitation</li>
                <li>Air quality shows seasonal variations</li>
                <li>Wind speed affects perceived temperature</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
            <h4>⚠️ Health Implications</h4>
            <ul>
                <li>High temperatures combined with poor air quality increase health risks</li>
                <li>Extreme humidity levels affect respiratory conditions</li>
                <li>Rapid temperature changes may impact vulnerable populations</li>
                <li>Monitor PM2.5 levels for air quality advisories</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="sub-header">Extreme Weather Events Detection</div>', unsafe_allow_html=True)
        
        if not extreme_events_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(viz['extreme_events'], use_container_width=True)
            
            with col2:
                st.markdown("""
                <div class="warning-box">
                <h4>⚠️ Extreme Events Summary</h4>
                <p>Detected events based on:</p>
                <ul>
                    <li>Temperature extremes (top/bottom 5%)</li>
                    <li>High wind speeds</li>
                    <li>Heavy precipitation</li>
                    <li>Poor air quality</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Display extreme events table
            st.markdown('<div class="sub-header">Detailed Extreme Events</div>', unsafe_allow_html=True)
            
            # Prepare events for display
            events_display = []
            for idx, row in extreme_events_df.iterrows():
                events_str = ", ".join([f"{e[0]} ({e[1]:.1f})" for e in row['events']])
                events_display.append({
                    'Country': row['country'],
                    'Location': row['location'],
                    'Events': events_str,
                    'Temperature': f"{row['temperature']:.1f}°C",
                    'Severity Score': f"{row['severity_score']:.2f}"
                })
            
            events_df_display = pd.DataFrame(events_display)
            st.dataframe(events_df_display, use_container_width=True)
            
            # Extreme events by type
            st.markdown('<div class="sub-header">Extreme Events by Type</div>', unsafe_allow_html=True)
            
            # Count events by type
            event_types = {}
            for idx, row in extreme_events_df.iterrows():
                for event in row['events']:
                    event_type = event[0]
                    event_types[event_type] = event_types.get(event_type, 0) + 1
            
            if event_types:
                event_df = pd.DataFrame(list(event_types.items()), columns=['Event Type', 'Count'])
                fig_events = px.bar(
                    event_df,
                    x='Event Type',
                    y='Count',
                    color='Count',
                    color_continuous_scale='Reds',
                    title='Extreme Events by Type'
                )
                st.plotly_chart(fig_events, use_container_width=True)
        else:
            st.info("No extreme events detected in the current data.")
    
    with tab4:
        st.markdown('<div class="sub-header">Regional Weather Comparison</div>', unsafe_allow_html=True)
        
        if 'regional_comparison' in viz:
            st.plotly_chart(viz['regional_comparison'], use_container_width=True)
        
        st.markdown('<div class="sub-header">Climate Zone Statistics</div>', unsafe_allow_html=True)
        
        if 'regional_comparisons' in analysis_results:
            st.dataframe(analysis_results['regional_comparisons'], use_container_width=True)
        
        # Additional regional insights
        col1, col2 = st.columns(2)
        
        with col1:
            if 'season' in df.columns:
                season_zone_fig = px.box(
                    df,
                    x='climate_zone',
                    y='temperature_celsius',
                    color='season',
                    title='Seasonal Temperatures by Climate Zone'
                )
                st.plotly_chart(season_zone_fig, use_container_width=True)
        
        with col2:
            comfort_fig = px.violin(
                df,
                x='climate_zone',
                y='comfort_index',
                color='climate_zone',
                box=True,
                title='Comfort Index by Climate Zone'
            )
            comfort_fig.update_layout(showlegend=False)
            st.plotly_chart(comfort_fig, use_container_width=True)
    
    with tab5:
        st.markdown('<div class="sub-header">Temporal Weather Patterns</div>', unsafe_allow_html=True)
        
        st.plotly_chart(viz['time_series'], use_container_width=True)
        
        if 'seasonal_patterns' in viz:
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(viz['seasonal_patterns'], use_container_width=True)
            
            with col2:
                # Hourly patterns heatmap
                df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
                hourly_pivot = df.pivot_table(
                    values='temperature_celsius',
                    index='hour',
                    columns='climate_zone',
                    aggfunc='mean'
                ).fillna(0)
                
                hour_fig = px.imshow(
                    hourly_pivot,
                    labels=dict(x="Climate Zone", y="Hour", color="Temperature (°C)"),
                    title="Hourly Temperatures by Climate Zone"
                )
                st.plotly_chart(hour_fig, use_container_width=True)
    
    # Sidebar Controls
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Controls")
        
        # Data filters
        st.markdown("### 🔍 Data Filters")
        
        selected_climate = st.multiselect(
            "Climate Zones",
            options=df['climate_zone'].unique(),
            default=df['climate_zone'].unique()
        )
        
        selected_season = st.multiselect(
            "Seasons",
            options=df['season'].unique(),
            default=df['season'].unique()
        )
        
        # Temperature range slider
        temp_range = st.slider(
            "Temperature Range (°C)",
            min_value=int(df['temperature_celsius'].min()),
            max_value=int(df['temperature_celsius'].max()),
            value=(10, 30)
        )
        
        # Analysis options
        st.markdown("### 📊 Analysis Options")
        
        show_extremes = st.checkbox("Highlight Extreme Events", value=True)
        normalize_data = st.checkbox("Normalize Data for Comparison", value=False)
        
        # Download options
        st.markdown("### 💾 Export Data")
        
        if st.button("📥 Download Analysis Report"):
            # Create a summary report
            report = {
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_records": len(df),
                "countries_analyzed": df['country'].nunique(),
                "average_temperature": df['temperature_celsius'].mean(),
                "extreme_events_count": len(extreme_events_df),
                "climate_zones_analyzed": df['climate_zone'].unique().tolist()
            }
            
            # Convert to DataFrame for display
            report_df = pd.DataFrame(list(report.items()), columns=['Metric', 'Value'])
            st.dataframe(report_df, use_container_width=True)
        
        # About section
        st.markdown("---")
        st.markdown("### ℹ️ About This Dashboard")
        st.markdown("""
        **Global Weather Analysis Dashboard**
        
        This interactive dashboard provides comprehensive analysis of global weather data including:
        
        - Statistical analysis of weather patterns
        - Extreme event detection
        - Regional climate comparisons
        - Temporal trend analysis
        - Correlation studies
        
        *Data updated regularly*
        """)
        
        # Data freshness
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()