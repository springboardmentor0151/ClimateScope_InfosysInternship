"""
ClimateScope Dashboard - Fixed Version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np

# Try to import scipy, fallback to numpy if not available
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    # Simple KDE approximation using numpy
    class SimpleKDE:
        @staticmethod
        def gaussian_kde(data):
            class KDE:
                def __init__(self, data):
                    self.data = np.array(data)
                    self.n = len(data)
                    # Use Silverman's rule of thumb for bandwidth
                    self.bandwidth = 1.06 * np.std(data) * (self.n ** (-1/5))
                
                def __call__(self, x):
                    x = np.array(x)
                    if len(x) == 0:
                        return x
                    if len(self.data) == 0:
                        return np.zeros_like(x)
                    
                    # Handle edge case where bandwidth is 0 or data has no variance
                    if self.bandwidth <= 0 or np.std(self.data) == 0:
                        # Return uniform distribution
                        return np.ones_like(x) / (x.max() - x.min() + 1e-10)
                    
                    # Use vectorized broadcasting for efficiency
                    # x is shape (n_x,), data is shape (n_data,)
                    # We want to compute for each x value
                    x_2d = x[:, np.newaxis]  # Shape: (n_x, 1)
                    data_2d = self.data[np.newaxis, :]  # Shape: (1, n_data)
                    
                    # Compute KDE using vectorized operations
                    diff = (x_2d - data_2d) / self.bandwidth
                    kernel = np.exp(-0.5 * diff ** 2)
                    result = np.sum(kernel, axis=1)  # Sum over data points for each x
                    
                    return result / (self.n * self.bandwidth * np.sqrt(2 * np.pi))
            return KDE(data)
    
    class stats:
        gaussian_kde = SimpleKDE.gaussian_kde

st.set_page_config(page_title="ClimateScope", page_icon="🌍", layout="wide")

PROCESSED_DATA_PATH = Path("data/processed")

@st.cache_data
def load_data():
    """Load and perform initial data processing"""
    df = pd.read_csv(PROCESSED_DATA_PATH / "cleaned_weather_data.csv")
    
    # Handle missing values
    df = handle_missing_values(df)
    
    # Convert date column to datetime
    df['last_updated_dt'] = pd.to_datetime(df['last_updated'], errors='coerce')
    
    # Ensure date column exists
    if 'date' not in df.columns:
        df['date'] = df['last_updated_dt'].dt.date
    
    # Clean inconsistent columns
    df = clean_inconsistent_columns(df)
    
    # Rename variables for clarity
    df = rename_variables_for_clarity(df)
    
    return df


def handle_missing_values(df):
    """Handle missing values in the dataset"""
    df = df.copy()
    
    # Fill numeric columns with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)
    
    # Fill categorical columns with mode
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            mode_value = df[col].mode()
            if len(mode_value) > 0:
                df[col].fillna(mode_value[0], inplace=True)
            else:
                df[col].fillna('Unknown', inplace=True)
    
    return df


def clean_inconsistent_columns(df):
    """Clean inconsistent data in columns"""
    df = df.copy()
    
    # Standardize country names (remove extra spaces, capitalize properly)
    if 'country' in df.columns:
        df['country'] = df['country'].str.strip().str.title()
    
    # Standardize location names
    if 'location_name' in df.columns:
        df['location_name'] = df['location_name'].str.strip().str.title()
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph', 
                      'air_quality_pm2.5', 'latitude', 'longitude']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    return df


def rename_variables_for_clarity(df):
    """Add descriptive aliases for variables (keep original names for compatibility)"""
    df = df.copy()
    
    # Create alias columns with more descriptive names (keep originals)
    if 'precip_mm' in df.columns:
        df['precipitation_mm'] = df['precip_mm']
    
    if 'wind_kph' in df.columns:
        df['wind_speed_kph'] = df['wind_kph']
    
    if 'air_quality_pm2.5' in df.columns:
        df['pm2_5_air_quality'] = df['air_quality_pm2.5']
    
    return df


def create_daily_aggregated_dataset(df):
    """Create daily aggregated dataset grouped by country and date"""
    df = df.copy()
    
    # Ensure we have the date column
    if 'date' not in df.columns and 'last_updated_dt' in df.columns:
        df['date'] = pd.to_datetime(df['last_updated_dt']).dt.date
    
    # Define aggregation functions for each column
    agg_dict = {
        'temperature_celsius': ['mean', 'min', 'max', 'std'],
        'humidity': ['mean', 'min', 'max'],
        'wind_speed_kph': ['mean', 'max'],
        'precipitation_mm': ['sum', 'mean', 'max'],
        'pm2_5_air_quality': ['mean', 'max'],
        'location_name': 'count'  # Count of observations
    }
    
    # Only include columns that exist in the dataframe
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    # Group by country and date
    daily_agg = df.groupby(['country', 'date']).agg(agg_dict).reset_index()
    
    # Flatten column names
    daily_agg.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                         for col in daily_agg.columns.values]
    
    # Rename count column
    if 'location_name_count' in daily_agg.columns:
        daily_agg = daily_agg.rename(columns={'location_name_count': 'num_observations'})
    
    return daily_agg


def create_monthly_aggregated_dataset(df):
    """Create monthly aggregated dataset grouped by country and month"""
    df = df.copy()
    
    # Ensure we have datetime column
    if 'last_updated_dt' not in df.columns:
        df['last_updated_dt'] = pd.to_datetime(df['last_updated'], errors='coerce')
    
    # Extract year and month
    df['year'] = df['last_updated_dt'].dt.year
    df['month'] = df['last_updated_dt'].dt.month
    df['year_month'] = df['last_updated_dt'].dt.to_period('M')
    
    # Define aggregation functions
    agg_dict = {
        'temperature_celsius': ['mean', 'min', 'max', 'std'],
        'humidity': ['mean', 'min', 'max'],
        'wind_speed_kph': ['mean', 'max'],
        'precipitation_mm': ['sum', 'mean', 'max'],
        'pm2_5_air_quality': ['mean', 'max'],
        'location_name': 'count'
    }
    
    # Only include columns that exist
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    # Group by country and year_month
    monthly_agg = df.groupby(['country', 'year_month']).agg(agg_dict).reset_index()
    
    # Flatten column names
    monthly_agg.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                           for col in monthly_agg.columns.values]
    
    # Rename count column
    if 'location_name_count' in monthly_agg.columns:
        monthly_agg = monthly_agg.rename(columns={'location_name_count': 'num_observations'})
    
    return monthly_agg


def calculate_heat_index(temp_c, humidity):
    """
    Calculate Heat Index (feels-like temperature in hot conditions)
    Formula: Heat Index = -8.78469475556 + 1.61139411*T + 2.33854883889*RH - 0.14611605*T*RH
    where T is temperature in Celsius and RH is relative humidity
    """
    # Convert to Fahrenheit for calculation
    temp_f = (temp_c * 9/5) + 32
    rh = humidity
    
    # Heat Index formula (Rothfusz equation)
    hi = (-42.379 + 2.04901523*temp_f + 10.14333127*rh 
          - 0.22475541*temp_f*rh - 6.83783e-3*temp_f**2 
          - 5.481717e-2*rh**2 + 1.22874e-3*temp_f**2*rh 
          + 8.5282e-4*temp_f*rh**2 - 1.99e-6*temp_f**2*rh**2)
    
    # Convert back to Celsius
    hi_c = (hi - 32) * 5/9
    return hi_c


def calculate_wind_chill(temp_c, wind_kph):
    """
    Calculate Wind Chill (feels-like temperature in cold conditions)
    Formula works when temperature <= 10°C and wind speed > 4.8 km/h
    """
    # Convert to metric units
    temp_c = np.where(temp_c <= 10, temp_c, np.nan)
    wind_ms = wind_kph / 3.6
    
    # Wind chill formula (metric version)
    wc = 13.12 + 0.6215*temp_c - 11.37*(wind_ms**0.16) + 0.3965*temp_c*(wind_ms**0.16)
    
    # Only valid when wind > 4.8 km/h and temp <= 10°C
    wc = np.where((wind_kph > 4.8) & (temp_c <= 10), wc, temp_c)
    
    return wc


def add_derived_metrics(df):
    """Add Heat Index and Wind Chill columns to dataframe"""
    df = df.copy()
    df['heat_index'] = calculate_heat_index(df['temperature_celsius'], df['humidity'])
    df['wind_chill'] = calculate_wind_chill(df['temperature_celsius'], df['wind_kph'])
    return df


def apply_moving_average(df, metric_col, window=7):
    """Apply 7-day moving average to a metric"""
    df = df.copy()
    df = df.sort_values('last_updated_dt')
    
    # Group by country and location if available, otherwise just by country
    if 'location_name' in df.columns:
        group_cols = ['country', 'location_name']
    else:
        group_cols = ['country']
    
    df[f'{metric_col}_ma7'] = df.groupby(group_cols)[metric_col].transform(
        lambda x: x.rolling(window=window, min_periods=1).mean()
    )
    return df


def normalize_data(series):
    """Normalize data using min-max scaling"""
    if series.min() == series.max():
        return series
    return (series - series.min()) / (series.max() - series.min())


def get_sidebar_filters(df):
    """Create and return all sidebar filters"""
    st.sidebar.header("🔍 Filters & Controls")
    
    # 1. Multi-select Country Filter
    st.sidebar.subheader("Country Selection")
    all_countries = sorted(df['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=all_countries if len(all_countries) <= 10 else [],
        help="Select one or more countries to analyze"
    )
    
    # 2. Date Range Filter
    st.sidebar.subheader("Date Range")
    min_date = df['last_updated_dt'].min().date()
    max_date = df['last_updated_dt'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Choose start and end dates for analysis"
    )
    
    # Handle different date_range return types from Streamlit
    if not isinstance(date_range, tuple):
        # Single date selected - convert to tuple
        if hasattr(date_range, 'date'):
            date_range = (date_range.date(), date_range.date())
        else:
            date_range = (date_range, date_range)
    elif len(date_range) == 1:
        # Only start date selected
        date_range = (date_range[0], max_date)
    elif len(date_range) == 2 and date_range[0] is None:
        # Only end date selected
        date_range = (min_date, date_range[1])
    
    # 3. Metric Selector
    st.sidebar.subheader("Metric Selection")
    base_metrics = {
        'Temperature (°C)': 'temperature_celsius',
        'Humidity (%)': 'humidity',
        'Precipitation (mm)': 'precip_mm',
        'Wind Speed (km/h)': 'wind_kph'
    }
    
    extreme_metrics = {
        'Heat Index': 'heat_index',
        'Wind Chill': 'wind_chill'
    }
    
    selected_base_metric = st.sidebar.selectbox(
        "Primary Metric",
        options=list(base_metrics.keys()),
        index=0,
        help="Select the main metric to analyze"
    )
    
    show_extreme_metrics = st.sidebar.checkbox(
        "Include Extreme Event Metrics",
        value=False,
        help="Include Heat Index and Wind Chill in analysis"
    )
    
    # 4. Monthly Averages Toggle
    st.sidebar.subheader("Aggregation Options")
    show_monthly_avg = st.sidebar.checkbox(
        "Show Monthly Averages",
        value=False,
        help="Display monthly aggregated data"
    )
    
    # 5. Seven-day Moving Averages Toggle
    show_ma7 = st.sidebar.checkbox(
        "Show 7-Day Moving Average",
        value=False,
        help="Apply 7-day moving average smoothing"
    )
    
    # 6. Time Aggregation Selector
    time_aggregation = st.sidebar.selectbox(
        "Time Aggregation",
        options=['Daily', 'Monthly', 'Seasonal'],
        index=0,
        help="Aggregate data by day, month, or season"
    )
    
    # 7. Threshold Input for Extreme Events
    st.sidebar.subheader("Extreme Events Threshold")
    extreme_threshold = st.sidebar.number_input(
        "Threshold Value",
        min_value=0.0,
        max_value=1000.0,
        value=40.0,
        step=1.0,
        help="Set threshold for detecting extreme events (varies by metric)"
    )
    
    # 8. Normalization Toggle
    normalize = st.sidebar.checkbox(
        "Normalize Data",
        value=False,
        help="Normalize metric values to 0-1 scale for comparison"
    )
    
    # 9. Range Slider Toggle (for time-series charts)
    st.sidebar.subheader("Chart Options")
    show_rangeslider = st.sidebar.checkbox(
        "Show Range Slider",
        value=False,
        help="Enable range slider for time-series charts (zoom and pan)"
    )
    
    return {
        'countries': selected_countries if selected_countries else all_countries,
        'date_range': date_range,
        'base_metric': base_metrics[selected_base_metric],
        'metric_label': selected_base_metric,
        'show_extreme_metrics': show_extreme_metrics,
        'extreme_metrics': extreme_metrics if show_extreme_metrics else {},
        'show_monthly_avg': show_monthly_avg,
        'show_ma7': show_ma7,
        'time_aggregation': time_aggregation,
        'extreme_threshold': extreme_threshold,
        'normalize': normalize,
        'show_rangeslider': show_rangeslider
    }


def filter_data(df, filters):
    """Apply all filters to the dataframe"""
    filtered_df = df.copy()
    
    # Filter by countries
    if filters['countries']:
        filtered_df = filtered_df[filtered_df['country'].isin(filters['countries'])]
    
    # Filter by date range
    date_range = filters['date_range']
    if date_range:
        # Handle different date_range formats
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            if start_date and end_date:
                # Convert to date if needed
                if hasattr(start_date, 'date'):
                    start_date = start_date.date()
                if hasattr(end_date, 'date'):
                    end_date = end_date.date()
                filtered_df = filtered_df[
                    (filtered_df['last_updated_dt'].dt.date >= start_date) &
                    (filtered_df['last_updated_dt'].dt.date <= end_date)
                ]
        elif hasattr(date_range, 'date'):
            # Single date
            single_date = date_range.date() if hasattr(date_range, 'date') else date_range
            filtered_df = filtered_df[filtered_df['last_updated_dt'].dt.date == single_date]
    
    return filtered_df


def get_country_iso3(country_name):
    """Convert country name to ISO-3 code"""
    # Common country name to ISO-3 mapping
    country_mapping = {
        'United States': 'USA', 'United Kingdom': 'GBR', 'Russia': 'RUS',
        'China': 'CHN', 'India': 'IND', 'Japan': 'JPN', 'Germany': 'DEU',
        'France': 'FRA', 'Italy': 'ITA', 'Brazil': 'BRA', 'Canada': 'CAN',
        'Australia': 'AUS', 'South Korea': 'KOR', 'Spain': 'ESP', 'Mexico': 'MEX',
        'Indonesia': 'IDN', 'Netherlands': 'NLD', 'Saudi Arabia': 'SAU',
        'Turkey': 'TUR', 'Switzerland': 'CHE', 'Argentina': 'ARG', 'Sweden': 'SWE',
        'Poland': 'POL', 'Belgium': 'BEL', 'Thailand': 'THA', 'Iran': 'IRN',
        'Austria': 'AUT', 'Norway': 'NOR', 'United Arab Emirates': 'ARE',
        'Israel': 'ISR', 'Ireland': 'IRL', 'Singapore': 'SGP', 'Malaysia': 'MYS',
        'South Africa': 'ZAF', 'Philippines': 'PHL', 'Denmark': 'DNK', 'Egypt': 'EGY',
        'Finland': 'FIN', 'Chile': 'CHL', 'Pakistan': 'PAK', 'Greece': 'GRC',
        'Portugal': 'PRT', 'Iraq': 'IRQ', 'Kazakhstan': 'KAZ', 'Algeria': 'DZA',
        'Qatar': 'QAT', 'Czech Republic': 'CZE', 'Romania': 'ROU', 'Peru': 'PER',
        'New Zealand': 'NZL', 'Vietnam': 'VNM', 'Bangladesh': 'BGD', 'Hungary': 'HUN',
        'Kuwait': 'KWT', 'Ukraine': 'UKR', 'Morocco': 'MAR', 'Slovakia': 'SVK',
        'Ecuador': 'ECU', 'Puerto Rico': 'PRI', 'Cuba': 'CUB', 'Oman': 'OMN',
        'Belarus': 'BLR', 'Azerbaijan': 'AZE', 'Sri Lanka': 'LKA', 'Myanmar': 'MMR',
        'Luxembourg': 'LUX', 'Dominican Republic': 'DOM', 'Uruguay': 'URY',
        'Bulgaria': 'BGR', 'Guatemala': 'GTM', 'Costa Rica': 'CRI', 'Tunisia': 'TUN',
        'Panama': 'PAN', 'Lebanon': 'LBN', 'Croatia': 'HRV', 'Lithuania': 'LTU',
        'Serbia': 'SRB', 'Slovenia': 'SVN', 'Bolivia': 'BOL', 'Libya': 'LBY',
        'Jordan': 'JOR', 'Paraguay': 'PRY', 'El Salvador': 'SLV', 'Turkmenistan': 'TKM',
        'Iceland': 'ISL', 'Nepal': 'NPL', 'Yemen': 'YEM', 'Jamaica': 'JAM',
        'Cambodia': 'KHM', 'Trinidad and Tobago': 'TTO', 'Latvia': 'LVA',
        'Estonia': 'EST', 'Bahrain': 'BHR', 'Cyprus': 'CYP', 'Honduras': 'HND',
        'Zimbabwe': 'ZWE', 'Senegal': 'SEN', 'Papua New Guinea': 'PNG', 'Zambia': 'ZMB',
        'Afghanistan': 'AFG', 'Bosnia and Herzegovina': 'BIH', 'Botswana': 'BWA',
        'Mali': 'MLI', 'Gabon': 'GAB', 'Albania': 'ALB', 'Nicaragua': 'NIC',
        'Mozambique': 'MOZ', 'Burkina Faso': 'BFA', 'Brunei': 'BRN', 'Madagascar': 'MDG',
        'Mauritius': 'MUS', 'Mongolia': 'MNG', 'Namibia': 'NAM', 'Rwanda': 'RWA',
        'Chad': 'TCD', 'Equatorial Guinea': 'GNQ', 'Guinea': 'GIN', 'Benin': 'BEN',
        'Haiti': 'HTI', 'Niger': 'NER', 'Malawi': 'MWI', 'Fiji': 'FJI',
        'Kyrgyzstan': 'KGZ', 'Moldova': 'MDA', 'Tajikistan': 'TJK', 'Togo': 'TGO',
        'Mauritania': 'MRT', 'Sierra Leone': 'SLE', 'Suriname': 'SUR', 'Bahamas': 'BHS',
        'Montenegro': 'MNE', 'Barbados': 'BRB', 'Belize': 'BLZ', 'Djibouti': 'DJI',
        'Guinea-Bissau': 'GNB', 'Liberia': 'LBR', 'Lesotho': 'LSO', 'Gambia': 'GMB',
        'Burundi': 'BDI', 'East Timor': 'TLS', 'Antigua and Barbuda': 'ATG',
        'Eritrea': 'ERI', 'Swaziland': 'SWZ', 'Maldives': 'MDV', 'Cape Verde': 'CPV',
        'Bhutan': 'BTN', 'Comoros': 'COM', 'Guyana': 'GUY', 'Solomon Islands': 'SLB',
        'Macao': 'MAC', 'Seychelles': 'SYC', 'Luxembourg': 'LUX', 'Malta': 'MLT',
        'Bahamas': 'BHS', 'Iceland': 'ISL', 'Barbados': 'BRB', 'Vanuatu': 'VUT',
        'Palau': 'PLW', 'San Marino': 'SMR', 'Saint Kitts and Nevis': 'KNA',
        'Marshall Islands': 'MHL', 'Liechtenstein': 'LIE', 'Monaco': 'MCO',
        'Saint Vincent and the Grenadines': 'VCT', 'Dominica': 'DMA', 'Tonga': 'TON',
        'Micronesia': 'FSM', 'Saint Lucia': 'LCA', 'Kiribati': 'KIR', 'Grenada': 'GRD',
        'Andorra': 'AND', 'Seychelles': 'SYC', 'Palau': 'PLW', 'Nauru': 'NRU',
        'Tuvalu': 'TUV', 'Vatican City': 'VAT'
    }
    return country_mapping.get(country_name, country_name[:3].upper() if len(country_name) >= 3 else country_name)


def add_iso3_codes(df):
    """Add ISO-3 country codes to dataframe"""
    df = df.copy()
    df['iso_alpha_3'] = df['country'].apply(get_country_iso3)
    return df


def get_plotly_config():
    """Get standard Plotly configuration with all interactive features enabled"""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'climatescope_chart',
            'height': None,
            'width': None,
            'scale': 2
        },
        'scrollZoom': True,  # Enable scroll to zoom
        'doubleClick': 'reset',  # Double-click to reset zoom
        'showTips': True
    }


def render_plotly_chart(fig, use_container_width=True, show_rangeslider=False):
    """Render Plotly chart with standard interactive features"""
    config = get_plotly_config()
    
    # Add range slider if requested and if x-axis is time-based
    if show_rangeslider:
        if hasattr(fig.layout, 'xaxis') and fig.layout.xaxis.type in ['date', 'linear']:
            fig.update_layout(
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.1),
                    type='date' if fig.layout.xaxis.type == 'date' else 'linear'
                )
            )
    
    st.plotly_chart(fig, use_container_width=use_container_width, config=config)


def render_plotly_chart(fig, use_container_width=True, show_rangeslider=False):
    """Render Plotly chart with standard interactive features"""
    config = get_plotly_config()
    
    # Add range slider if requested and if x-axis is time-based
    if show_rangeslider:
        if hasattr(fig.layout, 'xaxis') and fig.layout.xaxis.type in ['date', 'linear']:
            fig.update_layout(
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.1),
                    type='date' if fig.layout.xaxis.type == 'date' else 'linear'
                )
            )
    
    st.plotly_chart(fig, use_container_width=use_container_width, config=config)


def get_plotly_layout_updates():
    """Get standard layout updates for zoom and pan with dark theme"""
    return {
        'dragmode': 'zoom',  # Enable zoom and pan
        'hovermode': 'closest',  # Better hover interaction
        'plot_bgcolor': 'rgba(0,0,0,0)',  # Transparent plot background
        'paper_bgcolor': 'rgba(0,0,0,0)',  # Transparent paper background
        'margin': dict(l=0, r=0, t=0, b=0),  # Remove margins
        'xaxis': dict(
            rangeslider=dict(visible=False),
            type='linear',
            showgrid=False,  # Hide grid lines
            zeroline=False,  # Hide zero line
            showticklabels=False  # Hide axis labels
        ),
        'yaxis': dict(
            type='linear',
            showgrid=False,  # Hide grid lines
            zeroline=False,  # Hide zero line
            showticklabels=False  # Hide axis labels
        ),
        'geo': {
            'bgcolor': 'rgba(0,0,0,0)',  # Transparent background for geo
            'showframe': False,  # Remove frame/border
            'showcoastlines': False,  # Remove coastlines
            'projection': {'type': 'natural earth'}
        }
    }


def create_custom_hover_template(metric_col, metric_label, include_date=True, include_country=True):
    """Create custom hover template with country, date, and metric value"""
    template_parts = []
    
    if include_country:
        template_parts.append("<b>Country:</b> %{customdata[0]}")
    
    if include_date:
        template_parts.append("<b>Date:</b> %{customdata[1]}")
    
    template_parts.append(f"<b>{metric_label}:</b> %{{y:.2f}}")
    template_parts.append("<extra></extra>")
    
    return "<br>".join(template_parts)


def create_area_chart(df, x_col, y_col, title, color='#FF6B6B', height=400, 
                     hover_data=None, show_rangeslider=False, xaxis_title=None, yaxis_title=None):
    """Create an area chart with interactive features"""
    # Ensure data is clean and not empty
    df_clean = df[[x_col, y_col]].dropna()
    
    if len(df_clean) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for area chart",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title=title, height=height)
        return fig
    
    # Convert x-axis to categorical to maintain order
    if not pd.api.types.is_numeric_dtype(df_clean[x_col]):
        # If x_col is not numeric, ensure it's treated as categorical
        df_clean = df_clean.sort_values(x_col)
    
    fig = go.Figure()
    
    # Simple hover template with better formatting
    y_label = yaxis_title if yaxis_title else y_col
    hovertemplate = f"<b>{x_col}:</b> %{{x}}<br><b>{y_label}:</b> %{{y:.2f}}<extra></extra>"
    
    # Add trace with explicit data
    fig.add_trace(go.Scatter(
        x=df_clean[x_col],
        y=df_clean[y_col],
        fill='tozeroy',
        mode='lines',
        name=y_col,
        line=dict(color=color, width=2.5),
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
        hovertemplate=hovertemplate
    ))
    
    layout_updates = get_plotly_layout_updates()
    
    # Remove conflicting keys from layout_updates
    if 'plot_bgcolor' in layout_updates:
        layout_updates.pop('plot_bgcolor')
    if 'paper_bgcolor' in layout_updates:
        layout_updates.pop('paper_bgcolor')
    if 'margin' in layout_updates:
        layout_updates.pop('margin')
    if 'hovermode' in layout_updates:
        hovermode = layout_updates.pop('hovermode')
    else:
        hovermode = 'x unified'
    
    # Configure x-axis for categorical data
    if not pd.api.types.is_numeric_dtype(df_clean[x_col]):
        layout_updates['xaxis'] = {
            'type': 'category',
            'categoryorder': 'array',
            'categoryarray': df_clean[x_col].tolist()
        }
    
    # Check if we should add range slider (only for datetime data)
    if show_rangeslider and pd.api.types.is_datetime64_any_dtype(df_clean[x_col]):
        if 'xaxis' not in layout_updates:
            layout_updates['xaxis'] = {}
        layout_updates['xaxis']['rangeslider'] = dict(visible=True, thickness=0.1)
    
    # Update layout with all settings
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            y=1.0,
            yanchor='bottom',
            font=dict(
                size=20,
                color='white',
                family='Arial, sans-serif',
                weight='bold'
            ),
            pad=dict(t=0, b=40)
        ),
        height=height,
        showlegend=False,
        xaxis_title=xaxis_title if xaxis_title else x_col,
        yaxis_title=yaxis_title if yaxis_title else y_col,
        hovermode=hovermode,
        margin=dict(l=60, r=30, t=120, b=70, pad=0),
        plot_bgcolor='rgba(0,0,0,0.02)',
        paper_bgcolor='rgba(0,0,0,0)',
        **layout_updates
    )
    return fig


def create_box_plot(df, x_col, y_col, title, height=400):
    """Create a box plot with interactive features using Graph Objects"""
    # Ensure data is clean
    df_clean = df[[x_col, y_col]].dropna()
    
    if len(df_clean) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for box plot",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title=title, height=height)
        return fig
    
    # Create figure using Graph Objects
    fig = go.Figure()
    
    # Get unique categories
    categories = df_clean[x_col].unique()
    
    # Add a box trace for each category
    for category in categories:
        category_data = df_clean[df_clean[x_col] == category][y_col]
        
        fig.add_trace(go.Box(
            y=category_data,
            name=str(category),
            marker=dict(color='#FF6B6B'),
            line=dict(color='#FF6B6B'),
            fillcolor='rgba(255, 107, 107, 0.5)',
            boxmean=True,  # Show mean line
            hovertemplate="<b>%{fullData.name}</b><br>" +
                         "Q1: %{q1:.2f}<br>" +
                         "Median: %{median:.2f}<br>" +
                         "Q3: %{q3:.2f}<br>" +
                         "Min: %{lowerfence:.2f}<br>" +
                         "Max: %{upperfence:.2f}<br>" +
                         "<extra></extra>"
        ))
    
    # Update layout
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=x_col,
        yaxis_title=y_col,
        showlegend=False,
        **layout_updates
    )
    
    return fig


def create_violin_plot(df, x_col, y_col, title, height=400):
    """Create a violin plot with interactive features using Graph Objects"""
    # Ensure data is clean
    df_clean = df[[x_col, y_col]].dropna()
    
    if len(df_clean) == 0:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for violin plot",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title=title, height=height)
        return fig
    
    # Create figure using Graph Objects
    fig = go.Figure()
    
    # Get unique categories
    categories = df_clean[x_col].unique()
    
    # Add a violin trace for each category
    for category in categories:
        category_data = df_clean[df_clean[x_col] == category][y_col]
        
        fig.add_trace(go.Violin(
            y=category_data,
            name=str(category),
            marker=dict(color='#FF6B6B'),
            line=dict(color='#FF6B6B'),
            fillcolor='rgba(255, 107, 107, 0.5)',
            box_visible=True,  # Show box plot inside
            meanline_visible=True,  # Show mean line
            hovertemplate="<b>%{fullData.name}</b><br>" +
                         "Value: %{y:.2f}<br>" +
                         "<extra></extra>"
        ))
    
    # Update layout
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=x_col,
        yaxis_title=y_col,
        showlegend=False,
        violinmode='group',  # Group violins together
        **layout_updates
    )
    
    return fig


def create_density_plot(df, col, title, height=400):
    """Create a density plot (KDE) with interactive features"""
    data = df[col].dropna()
    
    if len(data) == 0:
        st.warning("No data available for density plot")
        return go.Figure()
    
    if len(data) < 2:
        st.warning("Insufficient data points for density plot")
        return go.Figure()
    
    try:
        kde = stats.gaussian_kde(data)
        x_range = np.linspace(data.min(), data.max(), 200)
        density = kde(x_range)
    except Exception as e:
        st.error(f"Error creating density plot: {str(e)}")
        # Fallback to histogram
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=data, nbinsx=40, name='Distribution'))
        layout_updates = get_plotly_layout_updates()
        fig.update_layout(title=title.replace('Density', 'Histogram'), height=height, **layout_updates)
        return fig
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_range,
        y=density,
        fill='tozeroy',
        mode='lines',
        name='Density',
        line=dict(color='#FF6B6B', width=2),
        fillcolor='rgba(255, 107, 107, 0.3)',
        hovertemplate=f"<b>{col}:</b> %{{x:.2f}}<br><b>Density:</b> %{{y:.4f}}<extra></extra>"
    ))
    
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(
        title=title,
        xaxis_title=col,
        yaxis_title='Density',
        height=height,
        showlegend=False,
        **layout_updates
    )
    return fig


def create_correlation_heatmap(df, metrics, title="Correlation Heatmap", height=500):
    """Create a correlation heatmap with interactive features"""
    corr_df = df[metrics].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_df.values,
        texttemplate='%{text:.2f}',
        textfont={"size":10},
        colorbar=dict(title="Correlation"),
        hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>"
    ))
    
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="",
        yaxis_title="",
        **layout_updates
    )
    return fig


def create_bubble_chart(df, x_col, y_col, size_col, color_col, title, height=400):
    """Create a bubble chart with custom hover"""
    hover_cols = []
    if 'country' in df.columns:
        hover_cols.append('country')
    if 'last_updated_dt' in df.columns:
        hover_cols.append('last_updated_dt')
    if 'location_name' in df.columns:
        hover_cols.append('location_name')
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        title=title,
        height=height,
        hover_data=hover_cols if hover_cols else []
    )
    
    # Update hover template
    if hover_cols:
        hover_template = f"<b>{x_col}:</b> %{{x:.2f}}<br>" + \
                        f"<b>{y_col}:</b> %{{y:.2f}}<br>"
        if 'country' in hover_cols:
            hover_template += "<b>Country:</b> %{customdata[0]}<br>"
        if 'last_updated_dt' in hover_cols:
            idx = hover_cols.index('last_updated_dt')
            hover_template += f"<b>Date:</b> %{{customdata[{idx}]}}<br>"
        hover_template += f"<b>{size_col}:</b> %{{marker.size}}<br>" + \
                         f"<b>{color_col}:</b> %{{marker.color:.2f}}<extra></extra>"
        fig.update_traces(hovertemplate=hover_template)
    
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(**layout_updates)
    return fig


def create_seasonal_heatmap(df, metric_col, title, height=400):
    """Create a seasonal heatmap"""
    df = df.copy()
    df['season'] = df['month'].apply(lambda x: 'Winter' if x in [12,1,2] else 
                                     'Spring' if x in [3,4,5] else
                                     'Summer' if x in [6,7,8] else 'Fall')
    
    seasonal_data = df.groupby(['country', 'season'])[metric_col].mean().reset_index()
    pivot_data = seasonal_data.pivot(index='country', columns='season', values=metric_col)
    
    # Limit to top countries by data points
    country_counts = df.groupby('country').size()
    top_countries = country_counts.nlargest(20).index
    pivot_data = pivot_data.loc[pivot_data.index.isin(top_countries)]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis',
        colorbar=dict(title=metric_col)
    ))
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="Season",
        yaxis_title="Country"
    )
    return fig


def create_ridgeline_plot(df, metric_col, group_col, title, height=600):
    """Create a ridgeline plot (density plots stacked)"""
    groups = df[group_col].unique()[:10]  # Limit to 10 groups
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    for i, group in enumerate(groups):
        group_data = df[df[group_col] == group][metric_col].dropna()
        if len(group_data) > 0:
            kde = stats.gaussian_kde(group_data)
            x_range = np.linspace(group_data.min(), group_data.max(), 100)
            density = kde(x_range)
            
            fig.add_trace(go.Scatter(
                x=x_range,
                y=density + i,  # Stack vertically
                fill='tozeroy',
                mode='lines',
                name=str(group),
                line=dict(color=colors[i % len(colors)], width=2),
                fillcolor=colors[i % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.3)')
            ))
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title=metric_col,
        yaxis_title="",
        showlegend=True
    )
    return fig


def create_extreme_events_tables(df):
    """Create tables for top 5 extreme events"""
    tables = {}
    
    # Top 5 Hottest Days
    hottest = df.nlargest(5, 'temperature_celsius')[
        ['last_updated_dt', 'country', 'location_name', 'temperature_celsius', 'humidity']
    ].copy()
    hottest.columns = ['Date', 'Country', 'Location', 'Temperature (°C)', 'Humidity (%)']
    tables['hottest'] = hottest
    
    # Top 5 Coldest Days
    coldest = df.nsmallest(5, 'temperature_celsius')[
        ['last_updated_dt', 'country', 'location_name', 'temperature_celsius', 'humidity']
    ].copy()
    coldest.columns = ['Date', 'Country', 'Location', 'Temperature (°C)', 'Humidity (%)']
    tables['coldest'] = coldest
    
    # Top 5 Windiest Days
    windiest = df.nlargest(5, 'wind_kph')[
        ['last_updated_dt', 'country', 'location_name', 'wind_kph', 'temperature_celsius']
    ].copy()
    windiest.columns = ['Date', 'Country', 'Location', 'Wind Speed (km/h)', 'Temperature (°C)']
    tables['windiest'] = windiest
    
    # Top 5 Rainiest Days
    rainiest = df.nlargest(5, 'precip_mm')[
        ['last_updated_dt', 'country', 'location_name', 'precip_mm', 'humidity']
    ].copy()
    rainiest.columns = ['Date', 'Country', 'Location', 'Precipitation (mm)', 'Humidity (%)']
    tables['rainiest'] = rainiest
    
    return tables


def create_extreme_events_timeline(df, threshold_dict, title="Extreme Events Over Time", height=400):
    """Create line chart of extreme event counts over months"""
    df = df.copy()
    df['year_month'] = df['last_updated_dt'].dt.to_period('M').astype(str)
    
    monthly_extremes = {}
    for event_name, (col, threshold, op) in threshold_dict.items():
        if op == '>':
            extreme_mask = df[col] > threshold
        else:
            extreme_mask = df[col] < threshold
        monthly_extremes[event_name] = df[extreme_mask].groupby('year_month').size()
    
    fig = go.Figure()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    for i, (event_name, counts) in enumerate(monthly_extremes.items()):
        fig.add_trace(go.Scatter(
            x=counts.index,
            y=counts.values,
            mode='lines+markers',
            name=event_name,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Number of Extreme Events",
        height=height,
        hovermode='x unified'
    )
    return fig


def create_regional_extremes_table(df, metric_col):
    """Create regional extreme events table"""
    regional = df.groupby('country').agg({
        metric_col: ['max', 'min', 'mean', 'std'],
        'location_name': 'count'
    }).reset_index()
    regional.columns = ['Country', 'Max', 'Min', 'Mean', 'Std Dev', 'Records']
    regional = regional.sort_values('Max', ascending=False)
    return regional.head(20)


def create_scatter_geo_map(df, metric_col, title, height=600):
    """Create scatter geo map with custom hover"""
    # Sample data if too large
    if len(df) > 5000:
        df = df.sample(n=5000, random_state=42)
    
    # Create figure with standard theme
    fig = px.scatter_geo(
        df,
        lat='latitude',
        lon='longitude',
        color=metric_col,
        hover_name='location_name',
        hover_data={
            'country': True, 
            'last_updated_dt': '|%Y-%m-%d %H:%M',
            metric_col: ':.2f',
            'latitude': ':.4f',
            'longitude': ':.4f'
        },
        title=title,
        color_continuous_scale='Viridis',
        height=height
    )
    
    # Update hover template for better formatting
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                     "<b>Country:</b> %{customdata[0]}<br>" +
                     "<b>Date:</b> %{customdata[1]}<br>" +
                     f"<b>{metric_col}:</b> %{{customdata[2]:.2f}}<br>" +
                     "<b>Lat:</b> %{customdata[3]:.4f}, <b>Lon:</b> %{customdata[4]:.4f}<extra></extra>"
    )
    
    # Update map appearance with standard theme
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue"
    )
    
    # Apply standard layout updates
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(**layout_updates)
    return fig


def create_choropleth_map(df, metric_col, title, height=600):
    """Create choropleth map with custom hover"""
    df = add_iso3_codes(df)
    country_avg = df.groupby(['country', 'iso_alpha_3'])[metric_col].mean().reset_index()
    
    # Add date range info if available
    if 'last_updated_dt' in df.columns:
        date_range = f"{df['last_updated_dt'].min().date()} to {df['last_updated_dt'].max().date()}"
    else:
        date_range = "N/A"
    
    fig = px.choropleth(
        country_avg,
        locations='iso_alpha_3',
        color=metric_col,
        hover_name='country',
        hover_data={
            metric_col: ':.2f', 
            'iso_alpha_3': False,
            'country': True
        },
        title=title,
        color_continuous_scale='Viridis',
        height=height,
        labels={metric_col: metric_col.replace('_', ' ').title()}
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                     f"<b>{metric_col}:</b> %{{customdata[0]:.2f}}<br>" +
                     f"<b>Date Range:</b> {date_range}<extra></extra>"
    )
    
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="lightgray"
    )
    
    layout_updates = get_plotly_layout_updates()
    fig.update_layout(**layout_updates)
    return fig


def show_global_analysis(df, filters):
    st.header("Global Weather Analysis")
    
    # Get metric column
    metric_col = filters['base_metric']
    metric_label = filters['metric_label']
    
    # Apply moving average if requested
    if filters['show_ma7']:
        df = apply_moving_average(df, metric_col, window=7)
        display_col = f'{metric_col}_ma7'
        display_label = f"{metric_label} (7-Day MA)"
    else:
        display_col = metric_col
        display_label = metric_label
    
    # Get metric value for display
    metric_value = df[display_col].mean()
    metric_unit = "°C" if "temperature" in metric_col or "heat" in metric_col or "chill" in metric_col else \
                  "%" if "humidity" in metric_col else \
                  "mm" if "precip" in metric_col else \
                  "km/h" if "wind" in metric_col else ""
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Countries", f"{df['country'].nunique()}")
    col2.metric("Locations", f"{df['location_name'].nunique()}")
    col3.metric(f"Avg {metric_label}", f"{metric_value:.1f}{metric_unit}")
    col4.metric("Avg PM2.5", f"{df['air_quality_pm2.5'].mean():.1f}")
    col5.metric("Records", f"{len(df):,}")
    
    st.markdown("---")
    
    # Trend Analysis - Line and Area Charts
    st.subheader(f"Trend Analysis - {metric_label}")
    col1, col2 = st.columns(2)
    
    with col1:
        # Line Chart
        if filters['time_aggregation'] == 'Daily':
            trend_data = df.groupby(df['last_updated_dt'].dt.date)[display_col].mean().reset_index()
            trend_data.columns = ['date', display_col]
            x_col = 'date'
        elif filters['time_aggregation'] == 'Monthly':
            trend_data = df.groupby('month')[display_col].mean().reset_index()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            trend_data['month_name'] = trend_data['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
            x_col = 'month_name'
        else:  # Seasonal
            df['season'] = df['month'].apply(lambda x: 'Winter' if x in [12,1,2] else 
                                             'Spring' if x in [3,4,5] else
                                             'Summer' if x in [6,7,8] else 'Fall')
            trend_data = df.groupby('season')[display_col].mean().reset_index()
            x_col = 'season'
        
        fig = px.line(trend_data, x=x_col, y=display_col, title=f'{metric_label} Trend (Line Chart)', markers=True)
        fig.update_traces(
            line_color='#FF6B6B', 
            line_width=3, 
            marker_size=8,
            hovertemplate=f"<b>{x_col}:</b> %{{x}}<br><b>{metric_label}:</b> %{{y:.2f}} {metric_unit}<extra></extra>"
        )
        layout_updates = get_plotly_layout_updates()
        if filters['show_rangeslider'] and x_col == 'date':
            layout_updates['xaxis']['rangeslider'] = dict(visible=True, thickness=0.1)
        fig.update_layout(height=400, xaxis_title=x_col.title(), yaxis_title=f'{metric_label} ({metric_unit})', **layout_updates)
        render_plotly_chart(fig, show_rangeslider=filters['show_rangeslider'] and x_col == 'date')
    
    with col2:
        # Area Chart
        fig = create_area_chart(trend_data, x_col, display_col, f'{metric_label} Trend (Area Chart)', 
                               height=400, show_rangeslider=filters['show_rangeslider'] and x_col == 'date')
        render_plotly_chart(fig, show_rangeslider=filters['show_rangeslider'] and x_col == 'date')
    
    st.markdown("---")
    
    # Distribution Analysis
    st.subheader(f"Distribution Analysis - {metric_label}")
    col1, col2 = st.columns(2)
    
    with col1:
        metric_data = df[display_col].dropna()
        
        # Normalize if requested
        if filters['normalize']:
            metric_data = normalize_data(metric_data)
            y_label = f"{metric_label} (Normalized)"
        else:
            y_label = metric_label
        
        # Histogram
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=metric_data,
            nbinsx=40,
            marker=dict(
                color='#FF6B6B',
                line=dict(color='white', width=1)
            )
        ))
        
        fig.update_layout(
            title=f'Histogram - {metric_label}',
            xaxis_title=y_label,
            yaxis_title='Number of Observations',
            height=400,
            showlegend=False
        )
        
        render_plotly_chart(fig)
        
        if not filters['normalize']:
            st.info(f"Most observations are between {metric_data.quantile(0.25):.2f} and {metric_data.quantile(0.75):.2f} {metric_unit}")
    
    with col2:
        # Box Plot
        if 'country' in df.columns and df['country'].nunique() <= 20:
            fig = create_box_plot(df, 'country', display_col, f'Box Plot - {metric_label} by Country', height=400)
        else:
            # Create box plot with sample countries
            top_countries = df.groupby('country').size().nlargest(10).index
            df_sample = df[df['country'].isin(top_countries)]
            fig = create_box_plot(df_sample, 'country', display_col, f'Box Plot - {metric_label} (Top 10 Countries)', height=400)
        render_plotly_chart(fig)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Violin Plot
        if 'country' in df.columns and df['country'].nunique() <= 15:
            fig = create_violin_plot(df, 'country', display_col, f'Violin Plot - {metric_label} by Country', height=400)
        else:
            top_countries = df.groupby('country').size().nlargest(10).index
            df_sample = df[df['country'].isin(top_countries)]
            fig = create_violin_plot(df_sample, 'country', display_col, f'Violin Plot - {metric_label} (Top 10 Countries)', height=400)
        render_plotly_chart(fig)
    
    with col2:
        # Density Plot
        fig = create_density_plot(df, display_col, f'Density Plot - {metric_label}', height=400)
        render_plotly_chart(fig)
    
    st.markdown("---")
    
    # Correlation Analysis
    st.subheader("Correlation Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Correlation Heatmap
        metrics_for_corr = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph', 'air_quality_pm2.5']
        available_metrics = [m for m in metrics_for_corr if m in df.columns]
        if len(available_metrics) >= 2:
            fig = create_correlation_heatmap(df, available_metrics, "Correlation Heatmap", height=400)
            render_plotly_chart(fig)
        else:
            st.info("Insufficient metrics for correlation analysis")
    
    with col2:
        # Bubble Chart
        sample_df = df.sample(n=min(1000, len(df)), random_state=42) if len(df) > 1000 else df
        fig = create_bubble_chart(
            sample_df,
            'temperature_celsius',
            'humidity',
            'wind_kph',
            'air_quality_pm2.5',
            'Bubble Chart: Temp vs Humidity (Size=Wind, Color=PM2.5)',
            height=400
        )
        render_plotly_chart(fig)
    
    st.markdown("---")
    
    # Seasonal Analysis
    st.subheader("Seasonal Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly Bar Chart
        monthly = df.groupby('month')[display_col].mean().reset_index()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly['month_name'] = monthly['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
        
        fig = px.bar(monthly, x='month_name', y=display_col, title=f'Monthly Bar Chart - {metric_label}', height=400)
        fig.update_traces(marker_color='#FF6B6B')
        fig.update_layout(xaxis_title='Month', yaxis_title=f'{metric_label} ({metric_unit})')
        render_plotly_chart(fig)
    
    with col2:
        # Seasonal Heatmap
        if df['country'].nunique() > 0:
            fig = create_seasonal_heatmap(df, display_col, f'Seasonal Heatmap - {metric_label}', height=400)
            render_plotly_chart(fig)
        else:
            st.info("Insufficient data for seasonal heatmap")
    
    # Ridgeline Plot
    if df['country'].nunique() >= 3:
        st.markdown("---")
        st.subheader("Ridgeline Plot - Distribution by Country")
        top_countries = df.groupby('country').size().nlargest(10).index
        df_ridge = df[df['country'].isin(top_countries)]
        fig = create_ridgeline_plot(df_ridge, display_col, 'country', f'Ridgeline Plot - {metric_label} by Country', height=600)
        render_plotly_chart(fig)
    
    st.markdown("---")
    
    # Regional Comparison
    st.subheader(f"Regional {metric_label} Comparison")
    
    regional = df.groupby('country').agg({
        display_col: 'mean',
        'location_name': 'count'
    }).reset_index()
    regional.columns = ['country', 'avg_metric', 'records']
    regional = regional[regional['records'] >= 10].sort_values('avg_metric')
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_high = regional.nlargest(10, 'avg_metric')
        fig = px.bar(
            top_high, 
            x='avg_metric', 
            y='country',
            orientation='h',
            title=f'Top 10 Highest {metric_label}',
            labels={'avg_metric': f'Avg {metric_label} ({metric_unit})', 'country': ''}
        )
        fig.update_traces(marker_color='#FF6B6B')
        fig.update_layout(height=400)
        render_plotly_chart(fig)
    
    with col2:
        top_low = regional.nsmallest(10, 'avg_metric')
        fig = px.bar(
            top_low, 
            x='avg_metric', 
            y='country',
            orientation='h',
            title=f'Top 10 Lowest {metric_label}',
            labels={'avg_metric': f'Avg {metric_label} ({metric_unit})', 'country': ''}
        )
        fig.update_traces(marker_color='#4ECDC4')
        fig.update_layout(height=400)
        render_plotly_chart(fig)
    
    st.markdown("---")
    
    # Extreme Events
    st.subheader("Extreme Weather Events")
    
    threshold = filters['extreme_threshold']
    metric_col = filters['base_metric']
    
    # Calculate extreme events based on selected metric and threshold
    if 'temperature' in metric_col:
        extreme_high = len(df[df[display_col] > threshold])
        extreme_low = len(df[df[display_col] < -threshold])
        extremes = {
            f'Extreme High\n(>{threshold}{metric_unit})': extreme_high,
            f'Extreme Low\n(<{-threshold}{metric_unit})': extreme_low,
        }
    elif 'precip' in metric_col:
        extremes = {
            f'Heavy Rain\n(>{threshold}mm)': len(df[df[display_col] > threshold]),
        }
    elif 'wind' in metric_col:
        extremes = {
            f'High Wind\n(>{threshold}km/h)': len(df[df[display_col] > threshold]),
        }
    elif 'humidity' in metric_col:
        extremes = {
            f'High Humidity\n(>{threshold}%)': len(df[df[display_col] > threshold]),
            f'Low Humidity\n(<{threshold}%)': len(df[df[display_col] < threshold]),
        }
    else:
        extremes = {
            f'Extreme High\n(>{threshold})': len(df[df[display_col] > threshold]),
            f'Extreme Low\n(<{threshold})': len(df[df[display_col] < threshold]),
        }
    
    # Add extreme metrics if enabled
    if filters['show_extreme_metrics']:
        if 'heat_index' in filters['extreme_metrics']:
            hi_threshold = threshold + 5  # Heat index typically higher
            extremes[f'High Heat Index\n(>{hi_threshold}°C)'] = len(df[df['heat_index'] > hi_threshold])
        if 'wind_chill' in filters['extreme_metrics']:
            wc_threshold = -threshold  # Wind chill typically lower
            extremes[f'Low Wind Chill\n(<{wc_threshold}°C)'] = len(df[df['wind_chill'] < wc_threshold])
    
    # Always include air quality
    extremes['Poor Air Quality\n(PM2.5>100)'] = len(df[df['air_quality_pm2.5'] > 100])
    
    if extremes:
        fig = px.bar(
            x=list(extremes.keys()), 
            y=list(extremes.values()),
            title='Frequency of Extreme Weather Events',
            labels={'x': 'Event Type', 'y': 'Number of Events'},
            text=list(extremes.values())
        )
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
        fig.update_traces(marker_color=colors[:len(extremes)],
                         textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        render_plotly_chart(fig)
        
        if extremes:
            max_event = max(extremes, key=extremes.get)
            st.warning(f"Most Common: {max_event} with {extremes[max_event]:,} events ({extremes[max_event]/len(df)*100:.1f}% of data)")
    
    # Extreme Events Tables
    st.markdown("---")
    st.subheader("Top 5 Extreme Events")
    extreme_tables = create_extreme_events_tables(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 5 Hottest Days**")
        st.dataframe(extreme_tables['hottest'], use_container_width=True, hide_index=True)
        
        st.markdown("**Top 5 Coldest Days**")
        st.dataframe(extreme_tables['coldest'], use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Top 5 Windiest Days**")
        st.dataframe(extreme_tables['windiest'], use_container_width=True, hide_index=True)
        
        st.markdown("**Top 5 Rainiest Days**")
        st.dataframe(extreme_tables['rainiest'], use_container_width=True, hide_index=True)
    
    # Extreme Events Timeline
    st.markdown("---")
    st.subheader("Extreme Events Over Time")
    threshold_dict = {
        'Extreme Heat': ('temperature_celsius', 40, '>'),
        'Extreme Cold': ('temperature_celsius', -10, '<'),
        'Heavy Rain': ('precip_mm', 20, '>'),
        'High Wind': ('wind_kph', 50, '>')
    }
    fig = create_extreme_events_timeline(df, threshold_dict, "Monthly Extreme Events Count", height=400)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Regional Extreme Events Table
    st.markdown("---")
    st.subheader("Regional Extreme Events")
    regional_extremes = create_regional_extremes_table(df, display_col)
    st.dataframe(regional_extremes, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Geographic Visualization
    st.subheader("Geographic Visualization")
    
    # Check if latitude and longitude columns exist
    if 'latitude' in df.columns and 'longitude' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter Geo Map
            fig = create_scatter_geo_map(df, display_col, f'Scatter Geo Map - {metric_label}', height=500)
            render_plotly_chart(fig)
        
        with col2:
            # Choropleth Map
            fig = create_choropleth_map(df, display_col, f'Choropleth Map - {metric_label}', height=500)
            render_plotly_chart(fig)
    else:
        st.info("Geographic data (latitude/longitude) not available for mapping")


def show_country_analysis(df, filters):
    # Filter by selected countries (for country analysis, use first selected or all)
    if filters['countries']:
        countries_to_show = filters['countries'][:1] if len(filters['countries']) == 1 else filters['countries']
    else:
        countries_to_show = [df['country'].iloc[0]]
    
    country_df = df[df['country'].isin(countries_to_show)].copy()
    
    if len(country_df) == 0:
        st.error(f"No data available for selected countries")
        return
    
    country_name = countries_to_show[0] if len(countries_to_show) == 1 else f"{len(countries_to_show)} Countries"
    st.header(f"{country_name} - Climate Analysis")
    st.markdown(f"Analyzing **{len(country_df):,}** observations from **{country_df['location_name'].nunique()}** locations")
    
    # Get metric column
    metric_col = filters['base_metric']
    metric_label = filters['metric_label']
    
    # Apply moving average if requested
    if filters['show_ma7']:
        country_df = apply_moving_average(country_df, metric_col, window=7)
        display_col = f'{metric_col}_ma7'
        display_label = f"{metric_label} (7-Day MA)"
    else:
        display_col = metric_col
        display_label = metric_label
    
    metric_unit = "°C" if "temperature" in metric_col or "heat" in metric_col or "chill" in metric_col else \
                  "%" if "humidity" in metric_col else \
                  "mm" if "precip" in metric_col else \
                  "km/h" if "wind" in metric_col else ""
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Locations", f"{country_df['location_name'].nunique()}")
    col2.metric(f"Avg {metric_label}", f"{country_df[display_col].mean():.1f}{metric_unit}")
    col3.metric("Avg Humidity", f"{country_df['humidity'].mean():.0f}%")
    col4.metric("Avg PM2.5", f"{country_df['air_quality_pm2.5'].mean():.1f}")
    col5.metric("Records", f"{len(country_df):,}")
    
    st.markdown("---")
    
    # Metric Analysis
    st.subheader(f"{metric_label} Analysis in {country_name}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{metric_label} Distribution**")
        
        metric_data = country_df[display_col].dropna()
        
        # Normalize if requested
        if filters['normalize']:
            metric_data = normalize_data(metric_data)
            x_label = f"{metric_label} (Normalized)"
        else:
            x_label = f"{metric_label} ({metric_unit})"
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=metric_data,
            nbinsx=30,
            marker=dict(
                color='#FF6B6B',
                line=dict(color='white', width=1)
            )
        ))
        
        fig.update_layout(
            title=f'{metric_label} Distribution in {country_name}',
            xaxis_title=x_label,
            yaxis_title='Number of Days',
            height=350,
            showlegend=False
        )
        
        render_plotly_chart(fig)
        
        if not filters['normalize']:
            st.metric(f"{metric_label} Range", 
                     f"{metric_data.min():.2f} to {metric_data.max():.2f} {metric_unit}")
            if len(metric_data.mode()) > 0:
                st.caption(f"Total observations: {len(metric_data)} | Most common: {metric_data.mode().values[0]:.2f} {metric_unit}")
    
    with col2:
        st.markdown(f"**{metric_label} Trend**")
        
        if filters['time_aggregation'] == 'Monthly' or filters['show_monthly_avg']:
            if filters['time_aggregation'] == 'Seasonal':
                country_df['season'] = country_df['month'].apply(lambda x: 'Winter' if x in [12,1,2] else 
                                                                  'Spring' if x in [3,4,5] else
                                                                  'Summer' if x in [6,7,8] else 'Fall')
                trend_data = country_df.groupby('season')[display_col].mean().reset_index()
                x_col = 'season'
                title = f'Seasonal {metric_label} in {country_name}'
            else:
                trend_data = country_df.groupby('month')[display_col].mean().reset_index()
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                trend_data['month_name'] = trend_data['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
                x_col = 'month_name'
                title = f'Monthly {metric_label} in {country_name}'
            
            fig = px.line(
                trend_data, 
                x=x_col, 
                y=display_col,
                title=title,
                markers=True
            )
            fig.update_traces(line_color='#FF6B6B', line_width=3, marker_size=10)
            fig.update_layout(height=350, xaxis_title=x_col.title(), yaxis_title=f'{metric_label} ({metric_unit})')
            render_plotly_chart(fig)
            
            if filters['time_aggregation'] == 'Monthly':
                best = trend_data.loc[trend_data[display_col].idxmin(), x_col]
                worst = trend_data.loc[trend_data[display_col].idxmax(), x_col]
                st.success(f"Lowest: {best}")
                st.error(f"Highest: {worst}")
        else:
            # Daily trend
            daily = country_df.groupby(country_df['last_updated_dt'].dt.date)[display_col].mean().reset_index()
            daily.columns = ['date', display_col]
            
            fig = px.line(
                daily,
                x='date',
                y=display_col,
                title=f'Daily {metric_label} in {country_name}',
                markers=True
            )
            fig.update_traces(line_color='#FF6B6B', line_width=2)
            fig.update_layout(height=350, xaxis_title='Date', yaxis_title=f'{metric_label} ({metric_unit})')
            render_plotly_chart(fig)
    
    st.markdown("---")
    
    # Air Quality
    st.subheader(f"Air Quality in {country_name}")
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_aq = country_df.groupby('month')['air_quality_pm2.5'].mean().reset_index()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_aq['month_name'] = monthly_aq['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
        
        fig = px.line(
            monthly_aq, 
            x='month_name', 
            y='air_quality_pm2.5',
            title=f'Monthly Air Quality (PM2.5) in {country_name}',
            markers=True
        )
        fig.update_traces(line_color='#98D8C8', line_width=3, marker_size=10)
        fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Hazardous")
        fig.update_layout(height=350, xaxis_title='Month', yaxis_title='PM2.5 (μg/m³)')
        render_plotly_chart(fig)
        
        avg_pm25 = country_df['air_quality_pm2.5'].mean()
        if avg_pm25 > 100:
            st.error(f"Hazardous: {avg_pm25:.1f} μg/m³")
        elif avg_pm25 > 50:
            st.warning(f"Moderate: {avg_pm25:.1f} μg/m³")
        else:
            st.success(f"Good: {avg_pm25:.1f} μg/m³")
    
    with col2:
        # Sample for scatter
        sample = country_df.sample(n=min(500, len(country_df)), random_state=42)
        
        fig = px.scatter(
            sample, 
            x='temperature_celsius', 
            y='humidity',
            color='air_quality_pm2.5',
            title=f'Temperature vs Humidity in {country_name}',
            labels={'temperature_celsius': 'Temperature (°C)', 
                   'humidity': 'Humidity (%)',
                   'air_quality_pm2.5': 'PM2.5'},
            color_continuous_scale='Viridis'
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(height=350)
        render_plotly_chart(fig)
        
        corr = country_df[['temperature_celsius', 'humidity']].corr().iloc[0, 1]
        st.info(f"Correlation: {corr:.2f}")
    
    st.markdown("---")
    
    # Extreme Events
    st.subheader(f"Extreme Events in {country_name}")
    
    threshold = filters['extreme_threshold']
    
    col1, col2, col3 = st.columns(3)
    
    extreme_high = len(country_df[country_df[display_col] > threshold])
    col1.metric(f"Extreme High ({metric_label})", f"{extreme_high}", 
               delta=f"{(extreme_high/len(country_df)*100):.1f}%")
    
    poor_aq = len(country_df[country_df['air_quality_pm2.5'] > 100])
    col2.metric("Poor Air Quality", f"{poor_aq}",
               delta=f"{(poor_aq/len(country_df)*100):.1f}%")
    
    if 'wind' in metric_col:
        high_wind = len(country_df[country_df['wind_kph'] > threshold])
        col3.metric("High Wind", f"{high_wind}",
                   delta=f"{(high_wind/len(country_df)*100):.1f}%")
    elif filters['show_extreme_metrics'] and 'heat_index' in filters['extreme_metrics']:
        high_hi = len(country_df[country_df['heat_index'] > threshold + 5])
        col3.metric("High Heat Index", f"{high_hi}",
                   delta=f"{(high_hi/len(country_df)*100):.1f}%")
    else:
        extreme_low = len(country_df[country_df[display_col] < -threshold if 'temperature' in metric_col else country_df[display_col] < threshold])
        col3.metric(f"Extreme Low ({metric_label})", f"{extreme_low}",
                   delta=f"{(extreme_low/len(country_df)*100):.1f}%")
    
    # Locations table
    if country_df['location_name'].nunique() > 1:
        st.markdown("---")
        st.subheader(f"Locations in {country_name}")
        
        locations = country_df.groupby('location_name').agg({
            'temperature_celsius': 'mean',
            'humidity': 'mean',
            'air_quality_pm2.5': 'mean'
        }).round(1).reset_index()
        locations.columns = ['Location', 'Avg Temp (°C)', 'Avg Humidity (%)', 'Avg PM2.5']
        
        st.dataframe(locations, use_container_width=True, height=300)


def show_executive_dashboard(df, filters):
    """Executive Dashboard with today's snapshot, global map, metrics, and insights"""
    st.title("🌍 Executive Dashboard")
    st.markdown("**Real-time Global Weather Intelligence Overview**")
    
    # Get latest data for today's snapshot
    latest_date = df['last_updated_dt'].max().date()
    today_data = df[df['last_updated_dt'].dt.date == latest_date]
    
    # Today's Weather Snapshot
    st.header("📊 Today's Weather Snapshot")
    if len(today_data) > 0:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Locations Reporting", f"{today_data['location_name'].nunique()}")
        col2.metric("Avg Temperature", f"{today_data['temperature_celsius'].mean():.1f}°C")
        col3.metric("Avg Humidity", f"{today_data['humidity'].mean():.0f}%")
        col4.metric("Avg Wind Speed", f"{today_data['wind_kph'].mean():.1f} km/h")
        col5.metric("Date", latest_date.strftime("%Y-%m-%d"))
        
        # Global Map
        st.markdown("---")
        st.subheader("🌐 Global Weather Map")
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # Use latest data for map
            map_data = today_data if len(today_data) > 0 else df.sample(n=min(5000, len(df)), random_state=42)
            fig = create_scatter_geo_map(
                map_data, 
                filters['base_metric'], 
                f"Global {filters['metric_label']} Distribution - {latest_date}",
                height=600
            )
            render_plotly_chart(fig)
        else:
            st.info("Geographic data not available")
    else:
        st.warning(f"No data available for {latest_date}")
        # Use most recent available data
        latest_data = df.nlargest(1000, 'last_updated_dt')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Locations", f"{df['location_name'].nunique()}")
        col2.metric("Avg Temperature", f"{df['temperature_celsius'].mean():.1f}°C")
        col3.metric("Avg Humidity", f"{df['humidity'].mean():.0f}%")
        col4.metric("Avg Wind Speed", f"{df['wind_kph'].mean():.1f} km/h")
        col5.metric("Total Records", f"{len(df):,}")
    
    # Global Mean Metrics
    st.markdown("---")
    st.subheader("📈 Global Mean Metrics")
    metric_col = filters['base_metric']
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Temperature metrics
    if 'temperature' in metric_col:
        col1.metric("Global Avg Temp", f"{df['temperature_celsius'].mean():.1f}°C", 
                   delta=f"Range: {df['temperature_celsius'].min():.1f}°C to {df['temperature_celsius'].max():.1f}°C")
        col2.metric("Avg Humidity", f"{df['humidity'].mean():.1f}%")
        col3.metric("Avg Precipitation", f"{df['precip_mm'].mean():.2f} mm")
        col4.metric("Avg Wind Speed", f"{df['wind_kph'].mean():.1f} km/h")
    else:
        col1.metric(f"Global Avg {filters['metric_label']}", f"{df[metric_col].mean():.2f}")
        col2.metric("Avg Temperature", f"{df['temperature_celsius'].mean():.1f}°C")
        col3.metric("Avg Humidity", f"{df['humidity'].mean():.1f}%")
        col4.metric("Avg PM2.5", f"{df['air_quality_pm2.5'].mean():.1f}")
    
    # Key Insights Summary
    st.markdown("---")
    st.subheader("💡 Key Insights Summary")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("#### 🌡️ Temperature Insights")
        hottest_country = df.groupby('country')['temperature_celsius'].mean().idxmax()
        coldest_country = df.groupby('country')['temperature_celsius'].mean().idxmin()
        st.info(f"**Hottest Region:** {hottest_country} ({df[df['country']==hottest_country]['temperature_celsius'].mean():.1f}°C avg)")
        st.info(f"**Coldest Region:** {coldest_country} ({df[df['country']==coldest_country]['temperature_celsius'].mean():.1f}°C avg)")
        
        st.markdown("#### 🌧️ Precipitation Insights")
        rainiest_country = df.groupby('country')['precip_mm'].mean().idxmax()
        st.info(f"**Rainiest Region:** {rainiest_country} ({df[df['country']==rainiest_country]['precip_mm'].mean():.2f} mm avg)")
    
    with insights_col2:
        st.markdown("#### 💨 Wind Insights")
        windiest_country = df.groupby('country')['wind_kph'].mean().idxmax()
        st.info(f"**Windiest Region:** {windiest_country} ({df[df['country']==windiest_country]['wind_kph'].mean():.1f} km/h avg)")
        
        st.markdown("#### 🌬️ Air Quality Insights")
        worst_aq_country = df.groupby('country')['air_quality_pm2.5'].mean().idxmax()
        best_aq_country = df.groupby('country')['air_quality_pm2.5'].mean().idxmin()
        st.warning(f"**Worst Air Quality:** {worst_aq_country} ({df[df['country']==worst_aq_country]['air_quality_pm2.5'].mean():.1f} PM2.5)")
        st.success(f"**Best Air Quality:** {best_aq_country} ({df[df['country']==best_aq_country]['air_quality_pm2.5'].mean():.1f} PM2.5)")
        
        # Extreme events summary
        extreme_heat = len(df[df['temperature_celsius'] > 40])
        extreme_cold = len(df[df['temperature_celsius'] < -10])
        st.markdown("#### ⚠️ Extreme Events")
        st.error(f"**Extreme Heat Events:** {extreme_heat:,} ({extreme_heat/len(df)*100:.1f}%)")
        st.info(f"**Extreme Cold Events:** {extreme_cold:,} ({extreme_cold/len(df)*100:.1f}%)")


def show_statistical_analysis(df, filters):
    """Statistical Analysis page with descriptive stats and country comparisons"""
    st.title("📊 Statistical Analysis")
    st.markdown("**Comprehensive Statistical Analysis of Weather Data**")
    
    metric_col = filters['base_metric']
    metric_label = filters['metric_label']
    
    # Descriptive Statistics Table
    st.header("📋 Descriptive Statistics")
    
    stats_data = {
        'Metric': [metric_label, 'Temperature (°C)', 'Humidity (%)', 'Precipitation (mm)', 'Wind Speed (km/h)', 'PM2.5'],
        'Mean': [
            df[metric_col].mean(),
            df['temperature_celsius'].mean(),
            df['humidity'].mean(),
            df['precip_mm'].mean(),
            df['wind_kph'].mean(),
            df['air_quality_pm2.5'].mean()
        ],
        'Median': [
            df[metric_col].median(),
            df['temperature_celsius'].median(),
            df['humidity'].median(),
            df['precip_mm'].median(),
            df['wind_kph'].median(),
            df['air_quality_pm2.5'].median()
        ],
        'Std Dev': [
            df[metric_col].std(),
            df['temperature_celsius'].std(),
            df['humidity'].std(),
            df['precip_mm'].std(),
            df['wind_kph'].std(),
            df['air_quality_pm2.5'].std()
        ],
        'Min': [
            df[metric_col].min(),
            df['temperature_celsius'].min(),
            df['humidity'].min(),
            df['precip_mm'].min(),
            df['wind_kph'].min(),
            df['air_quality_pm2.5'].min()
        ],
        'Max': [
            df[metric_col].max(),
            df['temperature_celsius'].max(),
            df['humidity'].max(),
            df['precip_mm'].max(),
            df['wind_kph'].max(),
            df['air_quality_pm2.5'].max()
        ],
        'Q1 (25%)': [
            df[metric_col].quantile(0.25),
            df['temperature_celsius'].quantile(0.25),
            df['humidity'].quantile(0.25),
            df['precip_mm'].quantile(0.25),
            df['wind_kph'].quantile(0.25),
            df['air_quality_pm2.5'].quantile(0.25)
        ],
        'Q3 (75%)': [
            df[metric_col].quantile(0.75),
            df['temperature_celsius'].quantile(0.75),
            df['humidity'].quantile(0.75),
            df['precip_mm'].quantile(0.75),
            df['wind_kph'].quantile(0.75),
            df['air_quality_pm2.5'].quantile(0.75)
        ]
    }
    
    stats_df = pd.DataFrame(stats_data)
    stats_df = stats_df.round(2)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Country Comparison Bar Charts
    st.markdown("---")
    st.header("🌍 Country Comparison")
    
    # Get top countries by data points
    country_counts = df.groupby('country').size()
    top_countries = country_counts.nlargest(20).index
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature comparison
        country_temp = df[df['country'].isin(top_countries)].groupby('country')['temperature_celsius'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=country_temp.values,
            y=country_temp.index,
            orientation='h',
            title='Average Temperature by Country (Top 20)',
            labels={'x': 'Temperature (°C)', 'y': 'Country'}
        )
        fig.update_traces(marker_color='#FF6B6B')
        fig.update_layout(height=500)
        render_plotly_chart(fig)
    
    with col2:
        # Humidity comparison
        country_humidity = df[df['country'].isin(top_countries)].groupby('country')['humidity'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=country_humidity.values,
            y=country_humidity.index,
            orientation='h',
            title='Average Humidity by Country (Top 20)',
            labels={'x': 'Humidity (%)', 'y': 'Country'}
        )
        fig.update_traces(marker_color='#4ECDC4')
        fig.update_layout(height=500)
        render_plotly_chart(fig)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Wind speed comparison
        country_wind = df[df['country'].isin(top_countries)].groupby('country')['wind_kph'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=country_wind.values,
            y=country_wind.index,
            orientation='h',
            title='Average Wind Speed by Country (Top 20)',
            labels={'x': 'Wind Speed (km/h)', 'y': 'Country'}
        )
        fig.update_traces(marker_color='#45B7D1')
        fig.update_layout(height=500)
        render_plotly_chart(fig)
    
    with col2:
        # PM2.5 comparison
        country_pm25 = df[df['country'].isin(top_countries)].groupby('country')['air_quality_pm2.5'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=country_pm25.values,
            y=country_pm25.index,
            orientation='h',
            title='Average PM2.5 by Country (Top 20)',
            labels={'x': 'PM2.5 (μg/m³)', 'y': 'Country'}
        )
        fig.update_traces(marker_color='#98D8C8')
        fig.update_layout(height=500)
        render_plotly_chart(fig)


def show_climate_trends(df, filters):
    """Climate Trends page with all trend visualizations"""
    st.title("📈 Climate Trends")
    st.markdown("**Long-term Climate Patterns and Trends**")
    
    metric_col = filters['base_metric']
    metric_label = filters['metric_label']
    
    if filters['show_ma7']:
        df = apply_moving_average(df, metric_col, window=7)
        display_col = f'{metric_col}_ma7'
    else:
        display_col = metric_col
    
    metric_unit = "°C" if "temperature" in metric_col else "%" if "humidity" in metric_col else "mm" if "precip" in metric_col else "km/h" if "wind" in metric_col else ""
    
    # Area Chart
    st.header("📊 Trend Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly trend area chart with proper month ordering
        monthly = df.groupby('month')[display_col].mean().reset_index()
        months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly['month_name'] = monthly['month'].apply(lambda x: months_order[x-1] if 1 <= x <= 12 else f'M{x}')
        
        # Create a custom sort order for months
        month_order = {month: i for i, month in enumerate(months_order)}
        monthly['month_order'] = monthly['month_name'].map(month_order)
        monthly = monthly.sort_values('month_order')
        
        # Create the area chart
        fig = create_area_chart(
            monthly, 
            'month_name', 
            display_col, 
            f'Monthly {metric_label} Trend',
            xaxis_title='Month',
            yaxis_title=f'{metric_label} ({metric_unit})',
            height=400
        )
        render_plotly_chart(fig)
    
    with col2:
        # Heatmap
        st.subheader("Seasonal Heatmap")
        if df['country'].nunique() > 0:
            fig = create_seasonal_heatmap(df, display_col, f'Seasonal Heatmap - {metric_label}', height=400)
            render_plotly_chart(fig)
    
    # Distribution Charts
    st.markdown("---")
    st.header("📉 Distribution Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Box Plot
        top_countries = df.groupby('country').size().nlargest(15).index
        df_box = df[df['country'].isin(top_countries)]
        fig = create_box_plot(df_box, 'country', display_col, f'Box Plot - {metric_label} by Country', height=500)
        render_plotly_chart(fig)
    
    with col2:
        # Violin Plot
        fig = create_violin_plot(df_box, 'country', display_col, f'Violin Plot - {metric_label} by Country', height=500)
        render_plotly_chart(fig)
    
    # Radar Chart
    st.markdown("---")
    st.header("🎯 Multi-Metric Radar Chart")
    
    # Get top countries and create radar chart
    top_countries_radar = df.groupby('country').size().nlargest(8).index
    radar_data = df[df['country'].isin(top_countries_radar)].groupby('country').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'wind_kph': 'mean',
        'precip_mm': 'mean',
        'air_quality_pm2.5': 'mean'
    }).reset_index()
    
    # Normalize for radar chart (0-1 scale) - normalize across all countries
    metrics_for_radar = ['temperature_celsius', 'humidity', 'wind_kph', 'precip_mm', 'air_quality_pm2.5']
    for metric in metrics_for_radar:
        col_min = radar_data[metric].min()
        col_max = radar_data[metric].max()
        if col_max > col_min:
            radar_data[f'{metric}_norm'] = (radar_data[metric] - col_min) / (col_max - col_min)
        else:
            radar_data[f'{metric}_norm'] = 0.5
    
    fig = go.Figure()
    
    categories = ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation', 'PM2.5']
    colors = px.colors.qualitative.Set3
    
    for idx, row in radar_data.iterrows():
        country = row['country']
        values = [
            row['temperature_celsius_norm'],
            row['humidity_norm'],
            row['wind_kph_norm'],
            row['precip_mm_norm'],
            row['air_quality_pm2.5_norm']
        ]
        # Close the radar chart
        values.append(values[0])
        categories_plot = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_plot,
            fill='toself',
            name=country,
            line=dict(color=colors[idx % len(colors)], width=2)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickmode='linear',
                tick0=0,
                dtick=0.2
            )),
        showlegend=True,
        title="Multi-Metric Comparison (Normalized 0-1 Scale)",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})


def show_extreme_events_page(df, filters):
    """Dedicated Extreme Events page"""
    st.title("⚠️ Extreme Events Analysis")
    st.markdown("**Comprehensive Analysis of Extreme Weather Events**")
    
    # Top 5 Tables
    st.header("🏆 Top 5 Extreme Events")
    extreme_tables = create_extreme_events_tables(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Top 5 Hottest Days")
        st.dataframe(extreme_tables['hottest'], use_container_width=True, hide_index=True)
        
        st.markdown("#### ❄️ Top 5 Coldest Days")
        st.dataframe(extreme_tables['coldest'], use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 💨 Top 5 Windiest Days")
        st.dataframe(extreme_tables['windiest'], use_container_width=True, hide_index=True)
        
        st.markdown("#### 🌧️ Top 5 Rainiest Days")
        st.dataframe(extreme_tables['rainiest'], use_container_width=True, hide_index=True)
    
    # Monthly Extreme Events Line Chart
    st.markdown("---")
    st.header("📅 Extreme Events Timeline")
    threshold_dict = {
        'Extreme Heat (>40°C)': ('temperature_celsius', 40, '>'),
        'Extreme Cold (<-10°C)': ('temperature_celsius', -10, '<'),
        'Heavy Rain (>20mm)': ('precip_mm', 20, '>'),
        'High Wind (>50km/h)': ('wind_kph', 50, '>'),
        'Poor Air Quality (>100 PM2.5)': ('air_quality_pm2.5', 100, '>')
    }
    fig = create_extreme_events_timeline(df, threshold_dict, "Monthly Extreme Events Count", height=500)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    # Regional Extreme Events Table
    st.markdown("---")
    st.header("🌍 Regional Extreme Events")
    
    metric_col = filters['base_metric']
    regional_extremes = create_regional_extremes_table(df, metric_col)
    st.dataframe(regional_extremes, use_container_width=True, hide_index=True)
    
    # Extreme Events Frequency
    st.markdown("---")
    st.header("📊 Extreme Events Frequency Analysis")
    
    extremes = {
        'Extreme Heat\n(>40°C)': len(df[df['temperature_celsius'] > 40]),
        'Extreme Cold\n(<-10°C)': len(df[df['temperature_celsius'] < -10]),
        'Heavy Rain\n(>20mm)': len(df[df['precip_mm'] > 20]),
        'High Wind\n(>50km/h)': len(df[df['wind_kph'] > 50]),
        'Poor Air Quality\n(PM2.5>100)': len(df[df['air_quality_pm2.5'] > 100])
    }
    
    fig = px.bar(
        x=list(extremes.keys()), 
        y=list(extremes.values()),
        title='Frequency of Extreme Weather Events',
        labels={'x': 'Event Type', 'y': 'Number of Events'},
        text=list(extremes.values())
    )
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    fig.update_traces(marker_color=colors, textposition='outside')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})


def show_help_page():
    """Help and User Guide section"""
    st.title("❓ Help & User Guide")
    st.markdown("**ClimateScope Dashboard - User Guide**")
    
    st.markdown("---")
    st.header("📖 Getting Started")
    
    st.markdown("""
    ### Welcome to ClimateScope!
    
    ClimateScope is a comprehensive weather intelligence dashboard that provides global and country-specific 
    climate analysis. This guide will help you navigate and use all the features effectively.
    """)
    
    st.markdown("---")
    st.header("🗺️ Navigation")
    
    st.markdown("""
    The dashboard is organized into **5 main sections** accessible via the sidebar:
    
    1. **Executive Dashboard** - Overview with today's snapshot and key insights
    2. **Statistical Analysis** - Descriptive statistics and country comparisons
    3. **Climate Trends** - Long-term patterns and distribution analysis
    4. **Extreme Events** - Analysis of extreme weather conditions
    5. **Help** - This guide
    """)
    
    st.markdown("---")
    st.header("🎛️ Using Filters")
    
    st.markdown("""
    ### Sidebar Filters
    
    All pages share a common set of filters in the sidebar:
    
    - **Country Selection**: Multi-select dropdown to choose one or more countries
    - **Date Range**: Select start and end dates for analysis
    - **Primary Metric**: Choose the main metric to analyze (Temperature, Humidity, Precipitation, Wind Speed)
    - **Extreme Event Metrics**: Toggle to include Heat Index and Wind Chill
    - **Monthly Averages**: Show monthly aggregated data
    - **7-Day Moving Average**: Apply smoothing to time series
    - **Time Aggregation**: Choose Daily, Monthly, or Seasonal aggregation
    - **Extreme Events Threshold**: Set custom threshold for detecting extreme events
    - **Normalize Data**: Normalize values to 0-1 scale for comparison
    """)
    
    st.markdown("---")
    st.header("📊 Chart Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Trend Analysis
        - **Line Chart**: Time series trends
        - **Area Chart**: Filled area under trend line
        
        ### Distribution Analysis
        - **Histogram**: Frequency distribution
        - **Box Plot**: Quartiles and outliers
        - **Violin Plot**: Distribution shape
        - **Density Plot**: Probability density
        """)
    
    with col2:
        st.markdown("""
        ### Correlation Analysis
        - **Scatter Plot**: Two-variable relationships
        - **Correlation Heatmap**: Multi-metric correlations
        - **Bubble Chart**: Three-variable visualization
        
        ### Geographic
        - **Scatter Geo Map**: Point-based map
        - **Choropleth Map**: Country-level map
        """)
    
    st.markdown("---")
    st.header("💡 Tips & Tricks")
    
    st.markdown("""
    1. **Use filters strategically**: Start broad, then narrow down to specific countries or dates
    2. **Compare metrics**: Switch between different metrics to see relationships
    3. **Download charts**: Use the download button (camera icon) on any Plotly chart
    4. **Zoom and pan**: Click and drag on charts to zoom, double-click to reset
    5. **Hover for details**: Hover over data points to see exact values
    """)
    
    st.markdown("---")
    st.header("📞 Support")
    
    st.markdown("""
    ### Data Information
    - **Total Records**: 107,573 observations
    - **Countries**: 211 countries
    - **Locations**: 254 unique locations
    - **Time Range**: May 2024 to November 2025
    
    ### Technical Details
    - Built with Streamlit and Plotly
    - Real-time data filtering
    - Interactive visualizations
    - Responsive design
    """)
    
    st.markdown("---")
    st.info("💡 **Tip**: Use the sidebar filters to customize your analysis. All charts update automatically based on your selections!")


def show_data_processing_page(df):
    """Display data processing features and aggregated datasets"""
    st.title("📊 Data Processing Features")
    st.markdown("**View data cleaning, transformation, and aggregation processes**")
    
    st.markdown("---")
    
    # Data Processing Summary
    st.header("✅ Data Processing Pipeline")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Countries", f"{df['country'].nunique()}")
    
    with col2:
        st.metric("Locations", f"{df['location_name'].nunique()}")
        st.metric("Date Range", f"{(df['last_updated_dt'].max() - df['last_updated_dt'].min()).days} days")
    
    with col3:
        missing_count = df.isnull().sum().sum()
        st.metric("Missing Values", f"{missing_count}")
        st.metric("Duplicate Rows", f"{df.duplicated().sum()}")
    
    st.markdown("---")
    
    # Processing Steps
    st.header("🔧 Processing Steps Applied")
    
    steps = [
        ("✅", "**Handling Missing Values**", "Numeric columns filled with median, categorical with mode"),
        ("✅", "**Date Conversion**", "Converted 'last_updated' to datetime format"),
        ("✅", "**Data Cleaning**", "Standardized country/location names, removed duplicates"),
        ("✅", "**Variable Renaming**", "Added descriptive aliases (precipitation_mm, wind_speed_kph, pm2_5_air_quality)"),
        ("✅", "**Derived Metrics**", "Calculated Heat Index and Wind Chill"),
        ("✅", "**Country-Level Grouping**", "Data grouped by country for analysis")
    ]
    
    for icon, title, description in steps:
        st.markdown(f"{icon} {title}: {description}")
    
    st.markdown("---")
    
    # Daily Aggregated Dataset
    st.header("📅 Daily Aggregated Dataset")
    st.markdown("**Data aggregated by country and date**")
    
    with st.spinner("Creating daily aggregated dataset..."):
        daily_agg = create_daily_aggregated_dataset(df)
    
    st.success(f"✅ Created daily aggregated dataset with {len(daily_agg):,} rows")
    
    # Show sample
    st.subheader("Sample Data (First 10 rows)")
    st.dataframe(daily_agg.head(10), use_container_width=True)
    
    # Download button
    csv_daily = daily_agg.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Daily Aggregated Dataset (CSV)",
        data=csv_daily,
        file_name="daily_aggregated_weather_data.csv",
        mime="text/csv",
        help="Download the daily aggregated dataset"
    )
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Days", f"{daily_agg['date'].nunique():,}")
    with col2:
        st.metric("Countries", f"{daily_agg['country'].nunique()}")
    with col3:
        st.metric("Avg Observations/Day", f"{daily_agg['num_observations'].mean():.1f}")
    
    st.markdown("---")
    
    # Monthly Aggregated Dataset
    st.header("📆 Monthly Aggregated Dataset")
    st.markdown("**Data aggregated by country and month**")
    
    with st.spinner("Creating monthly aggregated dataset..."):
        monthly_agg = create_monthly_aggregated_dataset(df)
    
    st.success(f"✅ Created monthly aggregated dataset with {len(monthly_agg):,} rows")
    
    # Show sample
    st.subheader("Sample Data (First 10 rows)")
    st.dataframe(monthly_agg.head(10), use_container_width=True)
    
    # Download button
    csv_monthly = monthly_agg.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Monthly Aggregated Dataset (CSV)",
        data=csv_monthly,
        file_name="monthly_aggregated_weather_data.csv",
        mime="text/csv",
        help="Download the monthly aggregated dataset"
    )
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Months", f"{monthly_agg['year_month'].nunique():,}")
    with col2:
        st.metric("Countries", f"{monthly_agg['country'].nunique()}")
    with col3:
        st.metric("Avg Observations/Month", f"{monthly_agg['num_observations'].mean():.1f}")
    
    st.markdown("---")
    
    # Data Quality Report
    st.header("📋 Data Quality Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Missing Values by Column")
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if len(missing_data) > 0:
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Percentage': (missing_data.values / len(df) * 100).round(2)
            })
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No missing values found!")
    
    with col2:
        st.subheader("Data Types")
        dtypes_df = pd.DataFrame({
            'Column': df.dtypes.index,
            'Data Type': df.dtypes.values.astype(str)
        })
        st.dataframe(dtypes_df, use_container_width=True, hide_index=True, height=300)
    
    st.markdown("---")
    
    # Column Descriptions
    st.header("📖 Column Descriptions")
    
    descriptions = {
        'country': 'Country name',
        'location_name': 'City or location name',
        'latitude': 'Geographic latitude',
        'longitude': 'Geographic longitude',
        'last_updated': 'Timestamp of observation',
        'last_updated_dt': 'Datetime version of last_updated',
        'date': 'Date of observation',
        'temperature_celsius': 'Temperature in Celsius',
        'humidity': 'Relative humidity percentage',
        'precip_mm': 'Precipitation in millimeters',
        'precipitation_mm': 'Precipitation in millimeters (alias)',
        'wind_kph': 'Wind speed in kilometers per hour',
        'wind_speed_kph': 'Wind speed in kilometers per hour (alias)',
        'air_quality_pm2.5': 'PM2.5 air quality index',
        'pm2_5_air_quality': 'PM2.5 air quality index (alias)',
        'heat_index': 'Calculated heat index (feels-like temperature in hot conditions)',
        'wind_chill': 'Calculated wind chill (feels-like temperature in cold conditions)',
        'month': 'Month number (1-12)',
        'year': 'Year',
        'season': 'Season (Winter, Spring, Summer, Fall)'
    }
    
    desc_df = pd.DataFrame([
        {'Column': col, 'Description': desc, 'Present': '✅' if col in df.columns else '❌'}
        for col, desc in descriptions.items()
    ])
    
    st.dataframe(desc_df, use_container_width=True, hide_index=True, height=400)
    
    st.markdown("---")
    st.info("💡 **Tip**: Use the download buttons to export aggregated datasets for further analysis in Excel or other tools!")


def main():
    st.sidebar.title("🌍 ClimateScope")
    st.sidebar.markdown("**Weather Intelligence Dashboard**")
    
    # Real-time Refresh Button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Data", help="Reload data and refresh all visualizations"):
        st.cache_data.clear()
        st.rerun()
    
    # Page Navigation
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigate to:",
        ["Executive Dashboard", "Statistical Analysis", "Climate Trends", "Extreme Events", "Data Processing", "Help"]
    )
    
    # Load data
    df = load_data()
    df = add_derived_metrics(df)
    
    st.sidebar.markdown("---")
    
    # Get filters (only show on analysis pages, not help)
    if page != "Help":
        filters = get_sidebar_filters(df)
        filtered_df = filter_data(df, filters)
        
        if len(filtered_df) == 0:
            st.error("No data available for the selected filters. Please adjust your filter settings.")
            return
    else:
        filters = None
        filtered_df = df
    
    # Show selected page
    if page == "Executive Dashboard":
        show_executive_dashboard(filtered_df, filters)
    elif page == "Statistical Analysis":
        show_statistical_analysis(filtered_df, filters)
    elif page == "Climate Trends":
        show_climate_trends(filtered_df, filters)
    elif page == "Extreme Events":
        show_extreme_events_page(filtered_df, filters)
    elif page == "Data Processing":
        show_data_processing_page(df)  # Use unfiltered data
    elif page == "Help":
        show_help_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>ClimateScope | 107,573 Records | 211 Countries</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
