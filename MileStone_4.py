# Milestone 3 - Enhanced Version
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from scipy import stats
import calendar
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="ClimateScope - Global Weather Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }

    /* Sub Headers */
    .sub-header {
        font-size: 1.6rem;
        color: #2563EB;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
        border-left: 4px solid #10B981;
        padding: 10px 0 10px 15px;
        background: linear-gradient(90deg, rgba(16,185,129,0.05), transparent);
        border-radius: 0 5px 5px 0;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(0,0,0,0.15);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 8px 0;
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }

    /* Cards */
    .stats-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 10px 0;
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
    }

    .stats-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #F8FAFC;
        padding: 5px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #F1F5F9;
        border-radius: 6px;
        font-weight: 500;
        color: #64748B;
        transition: all 0.3s ease;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
    }

    /* Sidebar (Slider Bar) Background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }

    /*  SIDEBAR HEADING COLOR FIX */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #DC2626 !important;   /* RED */
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59,130,246,0.3);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .metric-value {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)
# /////////////////////////////////////////////////////////////
st.markdown("""
<style>

    /* ===================== SIDEBAR BACKGROUND ===================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%);
    }

    /* ===================== SIDEBAR HEADINGS ===================== */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #DC2626 !important;   /* RED */
        font-weight: 700;
    }

    /* ===================== SIDEBAR LABEL TEXT ===================== */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        color: #1E3A8A !important;  /* DARK BLUE */
    }

    /* ===================== SLIDER LABEL VALUE ===================== */
    section[data-testid="stSidebar"] .stSlider span {
        color: #DC2626 !important;  /* RED */
        font-weight: 600;
    }

    /* ===================== SLIDER TRACK ===================== */
    section[data-testid="stSidebar"] .stSlider > div > div > div > div {
        background-color: #F87171 !important; /* Light Red */
    }

    /* ===================== RADIO BUTTON TEXT ===================== */
    section[data-testid="stSidebar"] .stRadio label {
        color: #1E3A8A !important;
        font-weight: 500;
    }

    /* ===================== CHECKBOX TEXT ===================== */
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #1E3A8A !important;
        font-weight: 500;
    }

    /* ===================== SELECTBOX TEXT ===================== */
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #1E3A8A !important;
        font-weight: 600;
    }

    /* ===================== DATE INPUT TEXT ===================== */
    section[data-testid="stSidebar"] .stDateInput label {
        color: #1E3A8A !important;
        font-weight: 600;
    }

    /* ===================== ICON COLOR ===================== */
    section[data-testid="stSidebar"] svg {
        color: #DC2626 !important;
    }

    /* ===================== DIVIDER LINE ===================== */
    section[data-testid="stSidebar"] hr {
        border-color: #FCA5A5;
    }

</style>
""", unsafe_allow_html=True)


# ==================== DATA FUNCTIONS ====================
@st.cache_data
def load_enhanced_data():
    """Load and prepare enhanced dataset with more features"""
    np.random.seed(42)
    n_countries = 150
    n_days = 365  # One year of data
    n_locations = 2  # Multiple locations per country
    
    # Create lists of countries with ISO codes
    country_data = {
        'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Andorra': 'AND', 
        'Angola': 'AGO', 'Argentina': 'ARG', 'Australia': 'AUS', 'Austria': 'AUT',
        'Azerbaijan': 'AZE', 'Bahamas': 'BHS', 'Bahrain': 'BHR', 'Bangladesh': 'BGD',
        'Barbados': 'BRB', 'Belarus': 'BLR', 'Belgium': 'BEL', 'Belize': 'BLZ',
        'Benin': 'BEN', 'Bhutan': 'BTN', 'Bolivia': 'BOL', 'Brazil': 'BRA',
        'Canada': 'CAN', 'Chile': 'CHL', 'China': 'CHN', 'Colombia': 'COL',
        'Costa Rica': 'CRI', 'Croatia': 'HRV', 'Cuba': 'CUB', 'Cyprus': 'CYP',
        'Czech Republic': 'CZE', 'Denmark': 'DNK', 'Dominican Republic': 'DOM',
        'Ecuador': 'ECU', 'Egypt': 'EGY', 'Ethiopia': 'ETH', 'Finland': 'FIN',
        'France': 'FRA', 'Germany': 'DEU', 'Ghana': 'GHA', 'Greece': 'GRC',
        'Guatemala': 'GTM', 'India': 'IND', 'Indonesia': 'IDN', 'Iran': 'IRN',
        'Iraq': 'IRQ', 'Ireland': 'IRL', 'Israel': 'ISR', 'Italy': 'ITA',
        'Jamaica': 'JAM', 'Japan': 'JPN', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ',
        'Kenya': 'KEN', 'Kuwait': 'KWT', 'Lebanon': 'LBN', 'Madagascar': 'MDG',
        'Malaysia': 'MYS', 'Mali': 'MLI', 'Mexico': 'MEX', 'Mongolia': 'MNG',
        'Morocco': 'MAR', 'Mozambique': 'MOZ', 'Myanmar': 'MMR', 'Namibia': 'NAM',
        'Nepal': 'NPL', 'Netherlands': 'NLD', 'New Zealand': 'NZL', 'Nigeria': 'NGA',
        'Norway': 'NOR', 'Oman': 'OMN', 'Pakistan': 'PAK', 'Panama': 'PAN',
        'Peru': 'PER', 'Philippines': 'PHL', 'Poland': 'POL', 'Portugal': 'PRT',
        'Qatar': 'QAT', 'Romania': 'ROU', 'Russia': 'RUS', 'Saudi Arabia': 'SAU',
        'Senegal': 'SEN', 'Serbia': 'SRB', 'Singapore': 'SGP', 'South Africa': 'ZAF',
        'South Korea': 'KOR', 'Spain': 'ESP', 'Sri Lanka': 'LKA', 'Sweden': 'SWE',
        'Switzerland': 'CHE', 'Thailand': 'THA', 'Tunisia': 'TUN', 'Turkey': 'TUR',
        'Uganda': 'UGA', 'Ukraine': 'UKR', 'United Arab Emirates': 'ARE',
        'United Kingdom': 'GBR', 'United States': 'USA', 'Uruguay': 'URY',
        'Venezuela': 'VEN', 'Vietnam': 'VNM', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'
    }
    
    countries = list(country_data.keys())
    iso_codes = list(country_data.values())
    
    # Climate zones with weights
    climate_zones = ['Tropical', 'Northern Temperate', 'Southern Temperate', 'Polar', 'Arid']
    
    # Generate date range
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    data = []
    
    for country_idx, country in enumerate(countries[:n_countries]):
        iso_alpha = iso_codes[country_idx]
        climate_zone = np.random.choice(climate_zones, p=[0.25, 0.35, 0.15, 0.1, 0.15])
        
        # Set base parameters based on climate zone
        if climate_zone == 'Tropical':
            base_temp = np.random.uniform(24, 32)
            temp_range = 5
            base_humidity = np.random.uniform(65, 90)
            base_precip = np.random.uniform(50, 200)
        elif climate_zone == 'Northern Temperate':
            base_temp = np.random.uniform(8, 22)
            temp_range = 15
            base_humidity = np.random.uniform(55, 85)
            base_precip = np.random.uniform(30, 100)
        elif climate_zone == 'Southern Temperate':
            base_temp = np.random.uniform(6, 20)
            temp_range = 12
            base_humidity = np.random.uniform(60, 88)
            base_precip = np.random.uniform(40, 120)
        elif climate_zone == 'Polar':
            base_temp = np.random.uniform(-15, 5)
            temp_range = 8
            base_humidity = np.random.uniform(50, 80)
            base_precip = np.random.uniform(10, 50)
        else:  # Arid
            base_temp = np.random.uniform(20, 35)
            temp_range = 20
            base_humidity = np.random.uniform(15, 50)
            base_precip = np.random.uniform(0, 30)
        
        for location_idx in range(n_locations):
            location_name = f"{country} City {location_idx + 1}"
            lat = np.random.uniform(-60, 70)
            lon = np.random.uniform(-180, 180)
            
            for date in dates:
                # Seasonal variation
                day_of_year = date.timetuple().tm_yday
                seasonal_factor = np.sin(2 * np.pi * (day_of_year - 80) / 365)
                
                # Random weather patterns
                temp_variation = np.random.normal(0, temp_range/4)
                daily_temp = base_temp + seasonal_factor * temp_range/2 + temp_variation
                
                # Add some extreme temperatures randomly
                if np.random.random() < 0.02:  # 2% chance of extreme
                    daily_temp += np.random.choice([-15, 15])
                
                # Calculate derived metrics
                humidity = np.clip(base_humidity + np.random.normal(0, 10), 10, 100)
                wind_speed = np.random.uniform(0, 30) + np.abs(np.random.normal(0, 5))
                pressure = 1013 + np.random.normal(0, 15)
                
                # Precipitation with seasonal patterns
                precip_chance = 0.3 if climate_zone in ['Tropical', 'Southern Temperate'] else 0.2
                precipitation = np.random.exponential(5) if np.random.random() < precip_chance else 0
                
                # Add seasonal precipitation patterns
                if climate_zone == 'Tropical' and 150 <= day_of_year <= 300:
                    precipitation *= 1.5  # Rainy season
                
                # Air quality - worse in urban areas
                air_quality = np.random.exponential(30) + (location_idx * 10)
                
                # Calculate comfort index
                heat_index = daily_temp + 0.5 * (humidity / 100) * (daily_temp - 14.4)
                wind_chill = 13.12 + 0.6215 * daily_temp - 11.37 * (wind_speed**0.16) + 0.3965 * daily_temp * (wind_speed**0.16)
                
                comfort_index = 1 - (abs(22 - daily_temp) / 40 + abs(60 - humidity) / 100 + wind_speed / 50 + precipitation / 100)
                comfort_index = np.clip(comfort_index, 0, 1)
                
                # Determine season
                month = date.month
                if climate_zone in ['Northern Temperate', 'Polar']:
                    if month in [12, 1, 2]: season = 'Winter'
                    elif month in [3, 4, 5]: season = 'Spring'
                    elif month in [6, 7, 8]: season = 'Summer'
                    else: season = 'Autumn'
                elif climate_zone == 'Southern Temperate':
                    if month in [12, 1, 2]: season = 'Summer'
                    elif month in [3, 4, 5]: season = 'Autumn'
                    elif month in [6, 7, 8]: season = 'Winter'
                    else: season = 'Spring'
                else:
                    season = 'Dry' if precipitation < 10 else 'Wet'
                
                # Calculate 7-day moving average (simulated)
                moving_avg_temp = daily_temp + np.random.normal(0, 1)
                
                row = {
                    'country': country,
                    'iso_alpha': iso_alpha,
                    'location_name': location_name,
                    'latitude': lat,
                    'longitude': lon,
                    'date': date,
                    'year': date.year,
                    'month': month,
                    'month_name': date.strftime('%B'),
                    'day': date.day,
                    'day_of_week': date.strftime('%A'),
                    'day_of_year': day_of_year,
                    'season': season,
                    'climate_zone': climate_zone,
                    'temperature_celsius': round(daily_temp, 1),
                    'temperature_fahrenheit': round(daily_temp * 9/5 + 32, 1),
                    'humidity': round(humidity, 1),
                    'wind_kph': round(wind_speed, 1),
                    'pressure_mb': round(pressure, 1),
                    'precip_mm': round(precipitation, 1),
                    'air_quality_PM2.5': round(air_quality, 1),
                    'cloud_cover': np.random.uniform(0, 100),
                    'uv_index': np.random.uniform(0, 12),
                    'visibility_km': np.random.uniform(2, 20),
                    'heat_index_celsius': round(heat_index, 1),
                    'wind_chill_celsius': round(max(wind_chill, daily_temp), 1) if daily_temp < 10 else daily_temp,
                    'comfort_index': round(comfort_index, 3),
                    'moving_avg_7d_temp': round(moving_avg_temp, 1),
                    'is_extreme_temp': abs(daily_temp - base_temp) > temp_range * 1.5,
                    'is_extreme_precip': precipitation > base_precip * 3,
                    'is_extreme_wind': wind_speed > 25,
                    'weather_severity': round(
                        abs(daily_temp - 20) / 30 + 
                        precipitation / 100 + 
                        wind_speed / 50 + 
                        air_quality / 300, 3
                    )
                }
                data.append(row)
    
    df = pd.DataFrame(data)
    
    # Create additional calculated columns
    df['comfort_level'] = pd.cut(df['comfort_index'], 
                                  bins=[0, 0.4, 0.7, 1.0], 
                                  labels=['Uncomfortable', 'Moderate', 'Comfortable'])
    
    # Create extreme event flags
    extreme_conditions = (
        (df['temperature_celsius'] >= df['temperature_celsius'].quantile(0.95)) |
        (df['temperature_celsius'] <= df['temperature_celsius'].quantile(0.05)) |
        (df['precip_mm'] >= df['precip_mm'].quantile(0.95)) |
        (df['wind_kph'] >= df['wind_kph'].quantile(0.95)) |
        (df['air_quality_PM2.5'] >= df['air_quality_PM2.5'].quantile(0.90))
    )
    
    df['is_extreme_event'] = extreme_conditions
    
    # Add extreme event type
    def get_extreme_type(row):
        types = []
        if row['temperature_celsius'] >= df['temperature_celsius'].quantile(0.95):
            types.append('Heatwave')
        elif row['temperature_celsius'] <= df['temperature_celsius'].quantile(0.05):
            types.append('Cold Wave')
        if row['precip_mm'] >= df['precip_mm'].quantile(0.95):
            types.append('Heavy Rain')
        if row['wind_kph'] >= df['wind_kph'].quantile(0.95):
            types.append('High Wind')
        if row['air_quality_PM2.5'] >= df['air_quality_PM2.5'].quantile(0.90):
            types.append('Poor Air Quality')
        return ', '.join(types) if types else 'Normal'
    
    df['extreme_type'] = df.apply(get_extreme_type, axis=1)
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    return df

def prepare_aggregated_datasets(df):
    """Create aggregated datasets for different time periods"""
    
    # Daily aggregated data
    daily_agg = df.groupby(['date', 'country', 'iso_alpha', 'climate_zone']).agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'wind_kph': 'mean',
        'precip_mm': 'sum',
        'air_quality_PM2.5': 'mean',
        'comfort_index': 'mean',
        'weather_severity': 'mean',
        'is_extreme_event': 'sum'
    }).reset_index()
    
    # Monthly aggregated data
    monthly_agg = df.groupby(['year', 'month', 'month_name', 'country', 'iso_alpha', 'climate_zone']).agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'wind_kph': 'mean',
        'precip_mm': 'sum',
        'air_quality_PM2.5': 'mean',
        'comfort_index': 'mean',
        'weather_severity': 'mean',
        'is_extreme_event': 'sum'
    }).reset_index()
    
    # Country-level aggregated data
    country_agg = df.groupby(['country', 'iso_alpha', 'climate_zone']).agg({
        'temperature_celsius': ['mean', 'min', 'max', 'std'],
        'humidity': ['mean', 'min', 'max', 'std'],
        'wind_kph': ['mean', 'min', 'max', 'std'],
        'precip_mm': ['mean', 'sum', 'max', 'std'],
        'air_quality_PM2.5': ['mean', 'min', 'max', 'std'],
        'comfort_index': 'mean',
        'weather_severity': 'mean'
    }).reset_index()
    
    # Flatten MultiIndex columns
    country_agg.columns = ['_'.join(col).strip('_') for col in country_agg.columns.values]
    
    return {
        'daily': daily_agg,
        'monthly': monthly_agg,
        'country': country_agg,
        'raw': df
    }

# ==================== ANALYSIS FUNCTIONS ====================
def perform_comprehensive_analysis(df):
    """Perform comprehensive statistical analysis"""
    
    analysis_results = {
        'descriptive_stats': {},
        'correlations': {},
        'seasonal_patterns': {},
        'regional_comparisons': {},
        'extreme_analysis': {},
        'trend_analysis': {}
    }
    
    # 1. Descriptive Statistics
    numeric_cols = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb', 
                   'precip_mm', 'air_quality_PM2.5', 'comfort_index', 'weather_severity']
    
    desc_stats = df[numeric_cols].describe().round(2)
    analysis_results['descriptive_stats'] = desc_stats
    
    # 2. Correlation Analysis
    corr_matrix = df[numeric_cols].corr().round(3)
    analysis_results['correlations'] = corr_matrix
    
    # 3. Seasonal Patterns
    if 'month_name' in df.columns:
        monthly_stats = df.groupby('month_name')[numeric_cols].agg(['mean', 'std', 'min', 'max']).round(2)
        # Reorder by month
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_stats = monthly_stats.reindex(month_order, fill_value=0)
        analysis_results['seasonal_patterns'] = monthly_stats
    
    # 4. Regional Comparisons
    if 'climate_zone' in df.columns:
        regional_stats = df.groupby('climate_zone')[numeric_cols].agg(['mean', 'std', 'count']).round(2)
        analysis_results['regional_comparisons'] = regional_stats
    
    # 5. Extreme Event Analysis
    if 'is_extreme_event' in df.columns:
        extreme_stats = {
            'total_extreme_events': df['is_extreme_event'].sum(),
            'extreme_event_rate': df['is_extreme_event'].mean() * 100,
            'events_by_type': df['extreme_type'].value_counts(),
            'events_by_country': df.groupby('country')['is_extreme_event'].sum().sort_values(ascending=False).head(10)
        }
        analysis_results['extreme_analysis'] = extreme_stats
    
    # 6. Trend Analysis
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        monthly_trend = df.groupby(pd.Grouper(key='date', freq='M')).agg({
            'temperature_celsius': 'mean',
            'precip_mm': 'sum',
            'is_extreme_event': 'sum'
        }).round(2)
        analysis_results['trend_analysis'] = monthly_trend
    
    return analysis_results

def identify_extreme_events_enhanced(df, thresholds=None):
    """Identify extreme weather events with custom thresholds"""
    
    if thresholds is None:
        thresholds = {
            'heatwave': df['temperature_celsius'].quantile(0.95),
            'cold_wave': df['temperature_celsius'].quantile(0.05),
            'high_wind': df['wind_kph'].quantile(0.95),
            'heavy_rain': df['precip_mm'].quantile(0.95),
            'poor_air_quality': df['air_quality_PM2.5'].quantile(0.90),
        }
    
    extreme_events = []
    
    for idx, row in df.iterrows():
        events = []
        
        if row['temperature_celsius'] >= thresholds['heatwave']:
            events.append(('Heatwave', f"{row['temperature_celsius']:.1f}°C"))
        elif row['temperature_celsius'] <= thresholds['cold_wave']:
            events.append(('Cold Wave', f"{row['temperature_celsius']:.1f}°C"))
        
        if row['wind_kph'] >= thresholds['high_wind']:
            events.append(('High Wind', f"{row['wind_kph']:.1f} kph"))
        
        if row['precip_mm'] >= thresholds['heavy_rain']:
            events.append(('Heavy Rain', f"{row['precip_mm']:.1f} mm"))
        
        if row['air_quality_PM2.5'] >= thresholds['poor_air_quality']:
            events.append(('Poor Air Quality', f"{row['air_quality_PM2.5']:.1f} µg/m³"))
        
        if events:
            extreme_events.append({
                'date': row.get('date', 'N/A'),
                'country': row['country'],
                'iso_alpha': row.get('iso_alpha', ''),
                'location': row.get('location_name', 'Unknown'),
                'latitude': row.get('latitude', 0),
                'longitude': row.get('longitude', 0),
                'events': events,
                'temperature': row['temperature_celsius'],
                'humidity': row.get('humidity', 0),
                'wind_speed': row.get('wind_kph', 0),
                'precipitation': row.get('precip_mm', 0),
                'air_quality': row.get('air_quality_PM2.5', 0),
                'severity_score': row.get('weather_severity', 0),
                'climate_zone': row.get('climate_zone', 'Unknown')
            })
    
    return pd.DataFrame(extreme_events), thresholds

def calculate_derived_metrics(df):
    """Calculate additional derived metrics"""
    
    # Heat Index (simplified)
    df['heat_index'] = df.apply(
        lambda row: row['temperature_celsius'] + 0.5 * (row['humidity'] / 100) * (row['temperature_celsius'] - 14.4),
        axis=1
    )
    
    # Wind Chill
    df['wind_chill'] = df.apply(
        lambda row: 13.12 + 0.6215*row['temperature_celsius'] - 11.37*(row['wind_kph']**0.16) + 
                   0.3965*row['temperature_celsius']*(row['wind_kph']**0.16) if row['temperature_celsius'] <= 10 else row['temperature_celsius'],
        axis=1
    )
    
    # Temperature anomaly (difference from country average)
    country_avg_temp = df.groupby('country')['temperature_celsius'].transform('mean')
    df['temp_anomaly'] = df['temperature_celsius'] - country_avg_temp
    
    # Moving averages
    df.sort_values(['country', 'date'], inplace=True)
    df['temp_7d_ma'] = df.groupby('country')['temperature_celsius'].transform(lambda x: x.rolling(7, 1).mean())
    df['precip_30d_sum'] = df.groupby('country')['precip_mm'].transform(lambda x: x.rolling(30, 1).sum())
    
    return df

# ==================== VISUALIZATION FUNCTIONS ====================
def create_executive_dashboard(df, agg_data, extreme_events):
    """Create executive dashboard visualizations"""
    
    viz = {}
    
    # 1. Global Temperature Choropleth
    country_avg_temp = agg_data['country']
    fig_map = px.choropleth(
        country_avg_temp,
        locations='iso_alpha',
        color='temperature_celsius_mean',
        hover_name='country',
        color_continuous_scale='RdYlBu_r',
        title=' Global Temperature Distribution (Country Averages)',
        labels={'temperature_celsius_mean': 'Avg Temp (°C)', 'iso_alpha': 'Country Code'},
        projection='natural earth'
    )
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_scale=1.1
        ),
        height=500,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    viz['global_temp_map'] = fig_map
    
    # 2. Key Metrics Cards (will be created in Streamlit)
    
    # 3. Time Series Trend
    if 'date' in df.columns:
        daily_avg = df.groupby('date').agg({
            'temperature_celsius': 'mean',
            'precip_mm': 'sum',
            'is_extreme_event': 'sum'
        }).reset_index()
        
        fig_trend = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Temperature Trend', 'Precipitation & Extreme Events'),
            vertical_spacing=0.15
        )
        
        # Temperature line
        fig_trend.add_trace(
            go.Scatter(x=daily_avg['date'], y=daily_avg['temperature_celsius'],
                      mode='lines', name='Temperature', line=dict(color='red', width=2)),
            row=1, col=1
        )
        
        # Precipitation bars
        fig_trend.add_trace(
            go.Bar(x=daily_avg['date'], y=daily_avg['precip_mm'],
                  name='Precipitation', marker_color='blue', opacity=0.6),
            row=2, col=1
        )
        
        # Extreme events line
        fig_trend.add_trace(
            go.Scatter(x=daily_avg['date'], y=daily_avg['is_extreme_event'],
                      mode='lines', name='Extreme Events', line=dict(color='orange', width=2)),
            row=2, col=1
        )
        
        fig_trend.update_layout(
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        fig_trend.update_xaxes(title_text="Date", row=2, col=1)
        fig_trend.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig_trend.update_yaxes(title_text="Precipitation (mm) / Events", row=2, col=1)
        
        viz['trend_analysis'] = fig_trend
    
    # 4. Top 5 Metrics Table
    top_hottest = df.nlargest(5, 'temperature_celsius')[['date', 'country', 'temperature_celsius']]
    top_coldest = df.nsmallest(5, 'temperature_celsius')[['date', 'country', 'temperature_celsius']]
    top_windiest = df.nlargest(5, 'wind_kph')[['date', 'country', 'wind_kph']]
    top_rainiest = df.nlargest(5, 'precip_mm')[['date', 'country', 'precip_mm']]
    
    viz['top_metrics'] = {
        'hottest': top_hottest,
        'coldest': top_coldest,
        'windiest': top_windiest,
        'rainiest': top_rainiest
    }
    
    return viz

def create_statistical_visualizations(df, analysis_results):
    """Create statistical analysis visualizations"""
    
    viz = {}
    
    # 1. Correlation Heatmap
    corr_matrix = analysis_results['correlations']
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu',
        title=' Correlation Matrix of Weather Variables',
        labels=dict(color="Correlation")
    )
    fig_corr.update_layout(height=500)
    viz['correlation_heatmap'] = fig_corr
    
    # 2. Distribution Plots
    fig_dist = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature Distribution', 'Humidity Distribution',
                       'Wind Speed Distribution', 'Precipitation Distribution'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Temperature histogram with KDE
    temp_hist = px.histogram(df, x='temperature_celsius', nbins=50, 
                             title='', marginal='box')
    for trace in temp_hist.data:
        fig_dist.add_trace(trace, row=1, col=1)
    
    # Humidity histogram
    hum_hist = px.histogram(df, x='humidity', nbins=50, title='', marginal='box')
    for trace in hum_hist.data:
        fig_dist.add_trace(trace, row=1, col=2)
    
    # Wind speed histogram
    wind_hist = px.histogram(df, x='wind_kph', nbins=50, title='', marginal='box')
    for trace in wind_hist.data:
        fig_dist.add_trace(trace, row=2, col=1)
    
    # Precipitation histogram
    precip_hist = px.histogram(df[df['precip_mm'] > 0], x='precip_mm', nbins=50, 
                               title='', marginal='box')
    for trace in precip_hist.data:
        fig_dist.add_trace(trace, row=2, col=2)
    
    fig_dist.update_layout(height=700, showlegend=False)
    viz['distributions'] = fig_dist
    
    # 3. Scatter Plot Matrix
    numeric_cols = ['temperature_celsius', 'humidity', 'wind_kph', 'precip_mm', 'air_quality_PM2.5']
    fig_scatter = px.scatter_matrix(
        df[numeric_cols],
        title='Scatter Plot Matrix of Key Variables',
        height=600
    )
    fig_scatter.update_traces(diagonal_visible=False)
    viz['scatter_matrix'] = fig_scatter
    
    # 4. Box Plots by Climate Zone
    fig_box = px.box(
        df,
        x='climate_zone',
        y='temperature_celsius',
        color='climate_zone',
        points='all',
        title=' Temperature Distribution by Climate Zone',
        labels={'temperature_celsius': 'Temperature (°C)', 'climate_zone': 'Climate Zone'}
    )
    fig_box.update_layout(height=500, showlegend=False)
    viz['box_plots'] = fig_box
    
    return viz

def create_climate_trend_visualizations(df, agg_data):
    """Create climate trend visualizations"""
    
    viz = {}
    
    # 1. Monthly Trends
    monthly_agg = agg_data['monthly']
    
    fig_monthly = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Monthly Temperature', 'Monthly Precipitation',
                       'Monthly Humidity', 'Monthly Wind Speed'),
        vertical_spacing=0.15
    )
    
    # Temperature by month
    monthly_temp = monthly_agg.groupby('month_name')['temperature_celsius'].mean().reset_index()
    fig_monthly.add_trace(
        go.Scatter(x=monthly_temp['month_name'], y=monthly_temp['temperature_celsius'],
                  mode='lines+markers', name='Temperature', line=dict(color='red', width=3)),
        row=1, col=1
    )
    
    # Precipitation by month
    monthly_precip = monthly_agg.groupby('month_name')['precip_mm'].sum().reset_index()
    fig_monthly.add_trace(
        go.Bar(x=monthly_precip['month_name'], y=monthly_precip['precip_mm'],
              name='Precipitation', marker_color='blue'),
        row=1, col=2
    )
    
    # Humidity by month
    monthly_hum = monthly_agg.groupby('month_name')['humidity'].mean().reset_index()
    fig_monthly.add_trace(
        go.Scatter(x=monthly_hum['month_name'], y=monthly_hum['humidity'],
                  mode='lines+markers', name='Humidity', line=dict(color='green', width=3)),
        row=2, col=1
    )
    
    # Wind speed by month
    monthly_wind = monthly_agg.groupby('month_name')['wind_kph'].mean().reset_index()
    fig_monthly.add_trace(
        go.Scatter(x=monthly_wind['month_name'], y=monthly_wind['wind_kph'],
                  mode='lines+markers', name='Wind Speed', line=dict(color='orange', width=3)),
        row=2, col=2
    )
    
    fig_monthly.update_layout(height=700, showlegend=True)
    viz['monthly_trends'] = fig_monthly
    
    # 2. Seasonal Heatmap
    if 'season' in df.columns:
        seasonal_heat = df.groupby(['season', 'climate_zone'])['temperature_celsius'].mean().unstack()
        fig_heatmap = px.imshow(
            seasonal_heat,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdYlBu_r',
            title='🌡️ Average Temperature by Season and Climate Zone',
            labels=dict(x="Climate Zone", y="Season", color="Temperature (°C)")
        )
        fig_heatmap.update_layout(height=400)
        viz['seasonal_heatmap'] = fig_heatmap
    
    # 3. Ridgeline Plot (Density by Climate Zone)
    climate_zones = df['climate_zone'].unique()
    fig_ridge = go.Figure()
    
    for i, zone in enumerate(climate_zones):
        zone_data = df[df['climate_zone'] == zone]['temperature_celsius']
        fig_ridge.add_trace(go.Violin(
            y=zone_data,
            name=zone,
            box_visible=True,
            meanline_visible=True,
            fillcolor=f'hsl({i*60}, 50%, 70%)',
            line_color=f'hsl({i*60}, 50%, 50%)',
            opacity=0.6
        ))
    
    fig_ridge.update_layout(
        title=' Temperature Distribution by Climate Zone (Violin Plot)',
        yaxis_title='Temperature (°C)',
        height=500,
        showlegend=True
    )
    viz['ridge_plot'] = fig_ridge
    
    # 4. Radar Chart for Climate Zone Characteristics
    radar_data = df.groupby('climate_zone').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'wind_kph': 'mean',
        'precip_mm': 'mean',
        'air_quality_PM2.5': 'mean',
        'comfort_index': 'mean'
    }).reset_index()
    
    # Normalize data for radar chart
    numeric_cols = ['temperature_celsius', 'humidity', 'wind_kph', 'precip_mm', 'air_quality_PM2.5', 'comfort_index']
    for col in numeric_cols:
        radar_data[col + '_norm'] = (radar_data[col] - radar_data[col].min()) / (radar_data[col].max() - radar_data[col].min()) * 100
    
    fig_radar = go.Figure()
    
    for _, row in radar_data.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[f'{col}_norm'] for col in numeric_cols],
            theta=numeric_cols,
            fill='toself',
            name=row['climate_zone']
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title=' Climate Zone Characteristics (Radar Chart)',
        height=500
    )
    viz['radar_chart'] = fig_radar
    
    return viz

def create_extreme_events_visualizations(extreme_events_df, df):
    """Create extreme events visualizations"""
    
    viz = {}
    
    if extreme_events_df.empty:
        return viz
    
    # 1. Extreme Events Frequency - FIXED ERROR HERE
    # Convert events string to list and explode
    if 'events' in extreme_events_df.columns:
        # Create a copy to avoid modifying the original
        events_expanded = extreme_events_df.copy()
        
        # Convert tuple events to strings and split
        event_list = []
        for events in events_expanded['events']:
            if isinstance(events, list):
                for event in events:
                    if isinstance(event, tuple):
                        event_list.append(event[0])  # Get event type from tuple
                    else:
                        event_list.append(str(event))
        
        # Count events
        from collections import Counter
        event_counts = Counter(event_list)
        
        # Create DataFrame for plotting
        event_counts_df = pd.DataFrame({
            'Event Type': list(event_counts.keys()),
            'Count': list(event_counts.values())
        })
        
        fig_freq = px.bar(
            event_counts_df,
            x='Event Type',
            y='Count',
            title=' Extreme Events Frequency by Type',
            labels={'Count': 'Count', 'Event Type': 'Event Type'},
            color='Count',
            color_continuous_scale='Reds'
        )
        fig_freq.update_layout(height=400)
        viz['event_frequency'] = fig_freq
    
    # 2. Monthly Extreme Events Trend
    if 'date' in extreme_events_df.columns:
        extreme_events_df['month'] = extreme_events_df['date'].dt.month
        monthly_events = extreme_events_df.groupby('month').size().reset_index(name='count')
        monthly_events['month_name'] = monthly_events['month'].apply(lambda x: calendar.month_abbr[x])
        
        fig_monthly_events = px.line(
            monthly_events,
            x='month_name',
            y='count',
            markers=True,
            title=' Monthly Extreme Events Trend',
            labels={'count': 'Number of Events', 'month_name': 'Month'}
        )
        fig_monthly_events.update_traces(line=dict(width=3, color='red'))
        fig_monthly_events.update_layout(height=400)
        viz['monthly_events_trend'] = fig_monthly_events
    
    # 3. Extreme Events Map
    if 'latitude' in extreme_events_df.columns and 'longitude' in extreme_events_df.columns:
        fig_extreme_map = px.scatter_geo(
            extreme_events_df,
            lat='latitude',
            lon='longitude',
            color='severity_score',
            size='severity_score',
            hover_name='country',
            hover_data=['events', 'temperature', 'precipitation', 'wind_speed'],
            title=' Extreme Events Global Distribution',
            projection='natural earth',
            color_continuous_scale='Reds'
        )
        fig_extreme_map.update_layout(height=500)
        viz['extreme_events_map'] = fig_extreme_map
    
    # 4. Top 5 Lists
    top_5_hottest = df.nlargest(5, 'temperature_celsius')[['date', 'country', 'temperature_celsius', 'location_name']]
    top_5_coldest = df.nsmallest(5, 'temperature_celsius')[['date', 'country', 'temperature_celsius', 'location_name']]
    top_5_windiest = df.nlargest(5, 'wind_kph')[['date', 'country', 'wind_kph', 'location_name']]
    top_5_rainiest = df.nlargest(5, 'precip_mm')[['date', 'country', 'precip_mm', 'location_name']]
    
    viz['top_5_lists'] = {
        'hottest': top_5_hottest,
        'coldest': top_5_coldest,
        'windiest': top_5_windiest,
        'rainiest': top_5_rainiest
    }
    
    # 5. Extreme Events by Country
    events_by_country = extreme_events_df.groupby('country').size().reset_index(name='count').sort_values('count', ascending=False).head(10)
    fig_country_events = px.bar(
        events_by_country,
        x='country',
        y='count',
        title=' Top 10 Countries by Extreme Events Count',
        labels={'count': 'Number of Events', 'country': 'Country'},
        color='count',
        color_continuous_scale='OrRd'
    )
    fig_country_events.update_layout(height=400)
    viz['events_by_country'] = fig_country_events
    
    return viz

def create_geographic_visualizations(agg_data):
    """Create geographic visualizations"""
    
    viz = {}
    
    # 1. Scatter Geo Map - FIXED: Need to extract latitude/longitude properly
    country_agg = agg_data['country'].copy()
    
    # For scatter_geo, we need proper lat/lon data
    # Since our aggregated data doesn't have lat/lon, we'll skip this or create synthetic coordinates
    # Alternatively, we can use choropleth which doesn't require coordinates
    
    # Create a simpler choropleth instead
    fig_scatter_geo = px.choropleth(
        country_agg,
        locations='iso_alpha',
        color='temperature_celsius_mean',
        hover_name='country',
        hover_data=['temperature_celsius_mean', 'precip_mm_sum', 'wind_kph_mean'],
        title=' Global Temperature Distribution',
        projection='natural earth',
        color_continuous_scale='RdYlBu_r'
    )
    fig_scatter_geo.update_layout(height=500)
    viz['scatter_geo'] = fig_scatter_geo
    
    # 2. Multiple Metric Choropleth
    # First, ensure we have the required columns
    required_cols = ['iso_alpha', 'country', 'temperature_celsius_mean', 
                     'precip_mm_sum', 'wind_kph_mean', 'air_quality_PM2.5_mean']
    
    if all(col in country_agg.columns for col in required_cols):
        fig_choropleth_grid = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperature', 'Precipitation', 'Wind Speed', 'Air Quality'),
            specs=[[{'type': 'choropleth'}, {'type': 'choropleth'}],
                   [{'type': 'choropleth'}, {'type': 'choropleth'}]]
        )
        
        # Temperature
        fig_choropleth_grid.add_trace(
            px.choropleth(
                country_agg,
                locations='iso_alpha',
                color='temperature_celsius_mean',
                hover_name='country',
                color_continuous_scale='RdYlBu_r'
            ).data[0],
            row=1, col=1
        )
        
        # Precipitation
        fig_choropleth_grid.add_trace(
            px.choropleth(
                country_agg,
                locations='iso_alpha',
                color='precip_mm_sum',
                hover_name='country',
                color_continuous_scale='Blues'
            ).data[0],
            row=1, col=2
        )
        
        # Wind Speed
        fig_choropleth_grid.add_trace(
            px.choropleth(
                country_agg,
                locations='iso_alpha',
                color='wind_kph_mean',
                hover_name='country',
                color_continuous_scale='Greens'
            ).data[0],
            row=2, col=1
        )
        
        # Air Quality
        fig_choropleth_grid.add_trace(
            px.choropleth(
                country_agg,
                locations='iso_alpha',
                color='air_quality_PM2.5_mean',
                hover_name='country',
                color_continuous_scale='Reds'
            ).data[0],
            row=2, col=2
        )
        
        fig_choropleth_grid.update_layout(
            height=800,
            showlegend=False,
            title_text=" Global Weather Metrics Comparison"
        )
        
        for i in range(4):
            fig_choropleth_grid.update_geos(
                showframe=False,
                showcoastlines=True,
                projection_type="natural earth",
                row=(i//2)+1, col=(i%2)+1
            )
        
        viz['choropleth_grid'] = fig_choropleth_grid
    
    return viz

# ==================== MAIN DASHBOARD ====================
def main():
    # Load data
    st.sidebar.markdown("##  Data Loading")
    with st.spinner("Loading and processing weather data..."):
        df_raw = load_enhanced_data()
        agg_data = prepare_aggregated_datasets(df_raw)
        df = agg_data['raw']
    
    # ==================== SIDEBAR CONTROLS ====================
    st.sidebar.markdown("---")
    st.sidebar.markdown("##  Dashboard Controls")
    
    # 1. Country Filter
    st.sidebar.markdown("### Country Filter")
    all_countries = sorted(df['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=all_countries[:5] if len(all_countries) > 5 else all_countries,
        help="Filter data by selected countries"
    )
    
    # 2. Date Range Filter
    st.sidebar.markdown("### Date Range")
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # 3. Metric Selector
    st.sidebar.markdown("### Metric Selector")
    metric_options = {
        'Temperature': 'temperature_celsius',
        'Humidity': 'humidity',
        'Precipitation': 'precip_mm',
        'Wind Speed': 'wind_kph',
        'Air Quality': 'air_quality_PM2.5',
        'Heat Index': 'heat_index_celsius',
        'Wind Chill': 'wind_chill_celsius',
        'Comfort Index': 'comfort_index',
        'Weather Severity': 'weather_severity'
    }
    
    selected_metric = st.sidebar.selectbox(
        "Primary Metric for Analysis",
        options=list(metric_options.keys()),
        index=0,
        help="Select the main metric to analyze"
    )
    selected_metric_col = metric_options[selected_metric]
    
    # 4. Threshold Configuration for Extreme Events
    st.sidebar.markdown("###  Extreme Events Thresholds")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        temp_threshold = st.slider(
            "Temperature Extreme (%)",
            min_value=90,
            max_value=99,
            value=95,
            help="Percentile threshold for temperature extremes"
        )
    
    with col2:
        precip_threshold = st.slider(
            "Precipitation Extreme (%)",
            min_value=90,
            max_value=99,
            value=95,
            help="Percentile threshold for precipitation extremes"
        )
    
    # 5. Chart-Level Filters
    st.sidebar.markdown("###  Chart Options")
    
    time_aggregation = st.sidebar.radio(
        "Time Aggregation",
        ["Daily", "Weekly", "Monthly", "Seasonal"],
        horizontal=True
    )
    
    normalize_data = st.sidebar.checkbox(
        "Normalize Data",
        value=False,
        help="Normalize data for better comparison across different scales"
    )
    
    show_trendline = st.sidebar.checkbox(
        "Show Trendline",
        value=True,
        help="Add trendline to time series charts"
    )
    
    # Apply filters
    df_filtered = df.copy()
    
    if selected_countries:
        df_filtered = df_filtered[df_filtered['country'].isin(selected_countries)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['date'] >= pd.to_datetime(start_date)) &
            (df_filtered['date'] <= pd.to_datetime(end_date))
        ]
    
    # Calculate derived metrics
    df_filtered = calculate_derived_metrics(df_filtered)
    
    # Perform analysis on filtered data
    with st.spinner("Performing statistical analysis..."):
        analysis_results = perform_comprehensive_analysis(df_filtered)
        
        # Calculate extreme events with custom thresholds
        thresholds = {
            'heatwave': df_filtered['temperature_celsius'].quantile(temp_threshold/100),
            'cold_wave': df_filtered['temperature_celsius'].quantile((100-temp_threshold)/100),
            'high_wind': df_filtered['wind_kph'].quantile(0.95),
            'heavy_rain': df_filtered['precip_mm'].quantile(precip_threshold/100),
            'poor_air_quality': df_filtered['air_quality_PM2.5'].quantile(0.90),
        }
        
        extreme_events_df, _ = identify_extreme_events_enhanced(df_filtered, thresholds)
    
    # ==================== DASHBOARD HEADER ====================
    st.markdown('<h1 class="main-header"> ClimateScope - Global Weather Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;">Comprehensive analysis of global weather patterns, trends, and extreme events</p>', unsafe_allow_html=True)
    
    # ==================== EXECUTIVE DASHBOARD ====================
    with st.expander(" Executive Dashboard Overview", expanded=True):
        st.markdown('<div class="sub-header">Key Performance Indicators</div>', unsafe_allow_html=True)
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_temp = df_filtered['temperature_celsius'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_temp:.1f}°C</div>
                <div class="metric-label">Average Temperature</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            extreme_count = len(extreme_events_df)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{extreme_count}</div>
                <div class="metric-label">Extreme Events</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            countries_count = df_filtered['country'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{countries_count}</div>
                <div class="metric-label">Countries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            comfort_avg = df_filtered['comfort_index'].mean() * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{comfort_avg:.0f}%</div>
                <div class="metric-label">Avg Comfort Index</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Today's Weather Snapshot
        st.markdown('<div class="sub-header">Today\'s Weather Snapshot</div>', unsafe_allow_html=True)
        
        # Get latest date data
        latest_date = df_filtered['date'].max()
        today_data = df_filtered[df_filtered['date'] == latest_date]
        
        if not today_data.empty:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Latest Update:** {latest_date.strftime('%B %d, %Y')}")
                st.markdown(f"**Countries Reporting:** {today_data['country'].nunique()}")
            
            with col2:
                today_avg_temp = today_data['temperature_celsius'].mean()
                st.metric("Average Temperature", f"{today_avg_temp:.1f}°C")
            
            with col3:
                today_extremes = today_data['is_extreme_event'].sum()
                st.metric("Extreme Events Today", today_extremes)
    
    # ==================== MAIN TABS ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Global Overview", 
        " Statistical Analysis", 
        " Climate Trends",
        " Extreme Events",
        " Geographic Analysis"
    ])
    
    # Create visualizations
    with st.spinner("Generating visualizations..."):
        exec_viz = create_executive_dashboard(df_filtered, agg_data, extreme_events_df)
        stat_viz = create_statistical_visualizations(df_filtered, analysis_results)
        trend_viz = create_climate_trend_visualizations(df_filtered, agg_data)
        extreme_viz = create_extreme_events_visualizations(extreme_events_df, df_filtered)
        geo_viz = create_geographic_visualizations(agg_data)
    
    # Tab 1: Global Overview
    with tab1:
        st.markdown('<div class="sub-header"> Global Temperature Distribution</div>', unsafe_allow_html=True)
        
        if 'global_temp_map' in exec_viz:
            st.plotly_chart(exec_viz['global_temp_map'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header"> Global Weather Trends</div>', unsafe_allow_html=True)
            if 'trend_analysis' in exec_viz:
                st.plotly_chart(exec_viz['trend_analysis'], use_container_width=True)
        
        with col2:
            st.markdown('<div class="sub-header"> Top 5 Records</div>', unsafe_allow_html=True)
            
            if 'top_metrics' in exec_viz:
                top_metrics = exec_viz['top_metrics']
                
                st.markdown("** Hottest Days**")
                st.dataframe(top_metrics['hottest'], use_container_width=True)
                
                st.markdown("** Coldest Days**")
                st.dataframe(top_metrics['coldest'], use_container_width=True)
        
        # Global Mean Metrics
        st.markdown('<div class="sub-header"> Global Mean Metrics</div>', unsafe_allow_html=True)
        
        metrics_df = pd.DataFrame({
            'Metric': ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation', 'Air Quality'],
            'Global Average': [
                f"{df_filtered['temperature_celsius'].mean():.1f}°C",
                f"{df_filtered['humidity'].mean():.0f}%",
                f"{df_filtered['wind_kph'].mean():.1f} kph",
                f"{df_filtered['precip_mm'].mean():.2f} mm",
                f"{df_filtered['air_quality_PM2.5'].mean():.1f} µg/m³"
            ],
            'Standard Deviation': [
                f"±{df_filtered['temperature_celsius'].std():.1f}",
                f"±{df_filtered['humidity'].std():.1f}",
                f"±{df_filtered['wind_kph'].std():.1f}",
                f"±{df_filtered['precip_mm'].std():.2f}",
                f"±{df_filtered['air_quality_PM2.5'].std():.1f}"
            ]
        })
        
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Tab 2: Statistical Analysis
    with tab2:
        st.markdown('<div class="sub-header"> Statistical Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Descriptive Statistics")
            st.dataframe(analysis_results['descriptive_stats'], use_container_width=True)
        
        with col2:
            st.markdown("#### Regional Comparisons")
            if 'regional_comparisons' in analysis_results:
                st.dataframe(analysis_results['regional_comparisons'], use_container_width=True)
        
        st.markdown('<div class="sub-header"> Correlation Analysis</div>', unsafe_allow_html=True)
        
        if 'correlation_heatmap' in stat_viz:
            st.plotly_chart(stat_viz['correlation_heatmap'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header"> Distribution Analysis</div>', unsafe_allow_html=True)
            if 'distributions' in stat_viz:
                st.plotly_chart(stat_viz['distributions'], use_container_width=True)
        
        with col2:
            st.markdown('<div class="sub-header"> Scatter Matrix</div>', unsafe_allow_html=True)
            if 'scatter_matrix' in stat_viz:
                st.plotly_chart(stat_viz['scatter_matrix'], use_container_width=True)
    
    # Tab 3: Climate Trends
    with tab3:
        st.markdown('<div class="sub-header"> Climate Trends Analysis</div>', unsafe_allow_html=True)
        
        if 'monthly_trends' in trend_viz:
            st.plotly_chart(trend_viz['monthly_trends'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'seasonal_heatmap' in trend_viz:
                st.markdown('<div class="sub-header"> Seasonal Patterns</div>', unsafe_allow_html=True)
                st.plotly_chart(trend_viz['seasonal_heatmap'], use_container_width=True)
        
        with col2:
            if 'ridge_plot' in trend_viz:
                st.markdown('<div class="sub-header"> Climate Zone Distributions</div>', unsafe_allow_html=True)
                st.plotly_chart(trend_viz['ridge_plot'], use_container_width=True)
        
        if 'radar_chart' in trend_viz:
            st.markdown('<div class="sub-header"> Climate Zone Characteristics</div>', unsafe_allow_html=True)
            st.plotly_chart(trend_viz['radar_chart'], use_container_width=True)
    
    # Tab 4: Extreme Events
    with tab4:
        st.markdown('<div class="sub-header"> Extreme Weather Events Analysis</div>', unsafe_allow_html=True)
        
        if extreme_events_df.empty:
            st.info("No extreme events detected with current thresholds.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'event_frequency' in extreme_viz:
                    st.plotly_chart(extreme_viz['event_frequency'], use_container_width=True)
            
            with col2:
                if 'monthly_events_trend' in extreme_viz:
                    st.plotly_chart(extreme_viz['monthly_events_trend'], use_container_width=True)
            
            if 'extreme_events_map' in extreme_viz:
                st.markdown('<div class="sub-header"> Extreme Events Global Distribution</div>', unsafe_allow_html=True)
                st.plotly_chart(extreme_viz['extreme_events_map'], use_container_width=True)
            
            st.markdown('<div class="sub-header"> Top 5 Extreme Records</div>', unsafe_allow_html=True)
            
            if 'top_5_lists' in extreme_viz:
                top_lists = extreme_viz['top_5_lists']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("** Hottest**")
                    st.dataframe(top_lists['hottest'][['country', 'temperature_celsius']], use_container_width=True)
                
                with col2:
                    st.markdown("**Coldest**")
                    st.dataframe(top_lists['coldest'][['country', 'temperature_celsius']], use_container_width=True)
                
                with col3:
                    st.markdown("** Windiest**")
                    st.dataframe(top_lists['windiest'][['country', 'wind_kph']], use_container_width=True)
                
                with col4:
                    st.markdown("** Rainiest**")
                    st.dataframe(top_lists['rainiest'][['country', 'precip_mm']], use_container_width=True)
            
            # Detailed Extreme Events Table
            st.markdown('<div class="sub-header"> Detailed Extreme Events</div>', unsafe_allow_html=True)
            
            if not extreme_events_df.empty:
                display_cols = ['date', 'country', 'events', 'temperature', 'precipitation', 'wind_speed', 'severity_score']
                display_df = extreme_events_df[display_cols].copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    display_df.sort_values('severity_score', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
    
    # Tab 5: Geographic Analysis
    with tab5:
        st.markdown('<div class="sub-header"> Geographic Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if 'scatter_geo' in geo_viz:
                st.plotly_chart(geo_viz['scatter_geo'], use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
            <h4> Map Interpretation</h4>
            <p>The choropleth map shows:</p>
            <ul>
                <li><strong>Color</strong>: Temperature gradient (red=hot, blue=cold)</li>
                <li><strong>Hover</strong>: Detailed country metrics</li>
                <li><strong>Projection</strong>: Natural Earth projection</li>
            </ul>
            <p>Redder colors indicate warmer regions.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Country statistics
            country_stats = agg_data['country'].sort_values('temperature_celsius_mean', ascending=False).head(10)
            st.markdown("** Top 10 Warmest Countries**")
            st.dataframe(country_stats[['country', 'temperature_celsius_mean']], use_container_width=True)
        
        if 'choropleth_grid' in geo_viz:
            st.markdown('<div class="sub-header"> Multi-Metric Comparison</div>', unsafe_allow_html=True)
            st.plotly_chart(geo_viz['choropleth_grid'], use_container_width=True)
    
    # ==================== SIDEBAR DOWNLOAD & HELP ====================
    st.sidebar.markdown("---")
    st.sidebar.markdown("##  Export Options")
    
    if st.sidebar.button(" Download Analysis Report", use_container_width=True):
        # Create summary report
        report_data = {
            'Analysis Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Total Records': len(df_filtered),
            'Countries Analyzed': df_filtered['country'].nunique(),
            'Date Range': f"{df_filtered['date'].min().strftime('%Y-%m-%d')} to {df_filtered['date'].max().strftime('%Y-%m-%d')}",
            'Average Temperature': f"{df_filtered['temperature_celsius'].mean():.2f}°C",
            'Extreme Events Count': len(extreme_events_df),
            'Primary Metric': selected_metric,
            'Climate Zones': ', '.join(sorted(df_filtered['climate_zone'].unique()))
        }
        
        report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
        st.sidebar.dataframe(report_df, use_container_width=True)
        
        # Provide download options
        csv = df_filtered.to_csv(index=False)
        st.sidebar.download_button(
            label=" Download Filtered Data (CSV)",
            data=csv,
            file_name=f"climate_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ℹ Help & Guide")
    
    with st.sidebar.expander(" User Guide"):
        st.markdown("""
        ### How to Use This Dashboard
        
        1. **Filter Data**: Use sidebar controls to select countries, date ranges, and metrics
        2. **Adjust Thresholds**: Set percentile thresholds for extreme event detection
        3. **Explore Tabs**: Navigate through different analysis sections
        4. **Interact with Charts**: Hover, zoom, and click on visualizations
        5. **Export Data**: Download reports and filtered datasets
        
        ### Key Features
        
        - **Global Overview**: Maps and key metrics
        - **Statistical Analysis**: Distributions and correlations
        - **Climate Trends**: Seasonal and monthly patterns
        - **Extreme Events**: Detection and analysis
        - **Geographic Analysis**: Spatial patterns and comparisons
        
        ### Tips
        
        - Use the date range slider to focus on specific periods
        - Adjust extreme event thresholds for sensitivity
        - Hover over charts for detailed information
        - Download data for further analysis
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; font-size: 0.9rem; padding: 20px;">
        <p> <strong>ClimateScope Global Weather Analytics Dashboard</strong> | 
        Last updated: {}  | </p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()