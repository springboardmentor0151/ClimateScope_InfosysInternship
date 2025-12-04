"""
ClimateScope Dashboard - Fixed Version
Author: Naman Mittal
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(page_title="ClimateScope", page_icon="🌍", layout="wide")

PROCESSED_DATA_PATH = Path("data/processed")

@st.cache_data
def load_data():
    df = pd.read_csv(PROCESSED_DATA_PATH / "cleaned_weather_data.csv")
    df['last_updated_dt'] = pd.to_datetime(df['last_updated'])
    return df


def show_global_analysis(df):
    st.header("Global Weather Analysis")
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Countries", f"{df['country'].nunique()}")
    col2.metric("Locations", f"{df['location_name'].nunique()}")
    col3.metric("Avg Temp", f"{df['temperature_celsius'].mean():.1f}°C")
    col4.metric("Avg PM2.5", f"{df['air_quality_pm2.5'].mean():.1f}")
    col5.metric("Records", f"{len(df):,}")
    
    st.markdown("---")
    
    # Temperature Distribution
    st.subheader("Global Temperature Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        temp_data = df['temperature_celsius'].dropna()
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=temp_data,
            nbinsx=40,
            marker=dict(
                color='#FF6B6B',
                line=dict(color='white', width=1)
            )
        ))
        
        fig.update_layout(
            title='Global Temperature Distribution',
            xaxis_title='Temperature (°C)',
            yaxis_title='Number of Observations',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.info(f"Most observations are between {temp_data.quantile(0.25):.1f}°C and {temp_data.quantile(0.75):.1f}°C")
    
    with col2:
        # Monthly trends
        monthly = df.groupby('month')['temperature_celsius'].mean().reset_index()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly['month_name'] = monthly['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
        
        fig = px.line(
            monthly, 
            x='month_name', 
            y='temperature_celsius',
            title='Average Temperature by Month',
            markers=True
        )
        fig.update_traces(line_color='#FF6B6B', line_width=3, marker_size=10)
        fig.update_layout(height=400, xaxis_title='Month', yaxis_title='Avg Temperature (°C)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        hottest = monthly.loc[monthly['temperature_celsius'].idxmax(), 'month_name']
        coldest = monthly.loc[monthly['temperature_celsius'].idxmin(), 'month_name']
        st.success(f"Coolest: {coldest} | Hottest: {hottest}")
    
    st.markdown("---")
    
    # Regional Comparison
    st.subheader("Regional Temperature Comparison")
    
    regional = df.groupby('country').agg({
        'temperature_celsius': 'mean',
        'location_name': 'count'
    }).reset_index()
    regional.columns = ['country', 'avg_temp', 'records']
    regional = regional[regional['records'] >= 100].sort_values('avg_temp')
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_hot = regional.nlargest(10, 'avg_temp')
        fig = px.bar(
            top_hot, 
            x='avg_temp', 
            y='country',
            orientation='h',
            title='Top 10 Hottest Countries',
            labels={'avg_temp': 'Avg Temperature (°C)', 'country': ''}
        )
        fig.update_traces(marker_color='#FF6B6B')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        top_cold = regional.nsmallest(10, 'avg_temp')
        fig = px.bar(
            top_cold, 
            x='avg_temp', 
            y='country',
            orientation='h',
            title='Top 10 Coldest Countries',
            labels={'avg_temp': 'Avg Temperature (°C)', 'country': ''}
        )
        fig.update_traces(marker_color='#4ECDC4')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # Extreme Events
    st.subheader("Extreme Weather Events")
    
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
    fig.update_traces(marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
                     textposition='outside')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    max_event = max(extremes, key=extremes.get)
    st.warning(f"Most Common: {max_event} with {extremes[max_event]:,} events ({extremes[max_event]/len(df)*100:.1f}% of data)")


def show_country_analysis(df, country):
    country_df = df[df['country'] == country].copy()
    
    if len(country_df) == 0:
        st.error(f"No data available for {country}")
        return
    
    st.header(f"{country} - Climate Analysis")
    st.markdown(f"Analyzing **{len(country_df):,}** observations from **{country_df['location_name'].nunique()}** locations")
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Locations", f"{country_df['location_name'].nunique()}")
    col2.metric("Avg Temp", f"{country_df['temperature_celsius'].mean():.1f}°C")
    col3.metric("Avg Humidity", f"{country_df['humidity'].mean():.0f}%")
    col4.metric("Avg PM2.5", f"{country_df['air_quality_pm2.5'].mean():.1f}")
    col5.metric("Records", f"{len(country_df):,}")
    
    st.markdown("---")
    
    # Temperature Analysis
    st.subheader(f"Temperature in {country}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Temperature Distribution**")
        
        temp_data = country_df['temperature_celsius'].dropna()
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=temp_data,
            nbinsx=30,
            marker=dict(
                color='#FF6B6B',
                line=dict(color='white', width=1)
            )
        ))
        
        fig.update_layout(
            title=f'Temperature Distribution in {country}',
            xaxis_title='Temperature (°C)',
            yaxis_title='Number of Days',
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.metric("Temperature Range", 
                 f"{temp_data.min():.1f}°C to {temp_data.max():.1f}°C")
        
        # Show data summary
        st.caption(f"Total observations: {len(temp_data)} | Most common: {temp_data.mode().values[0]:.1f}°C")
    
    with col2:
        st.markdown("**Monthly Temperature Trend**")
        monthly = country_df.groupby('month')['temperature_celsius'].mean().reset_index()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly['month_name'] = monthly['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
        
        fig = px.line(
            monthly, 
            x='month_name', 
            y='temperature_celsius',
            title=f'Monthly Temperature in {country}',
            markers=True
        )
        fig.update_traces(line_color='#FF6B6B', line_width=3, marker_size=10)
        fig.update_layout(height=350, xaxis_title='Month', yaxis_title='Temperature (°C)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        best = monthly.loc[monthly['temperature_celsius'].idxmin(), 'month_name']
        worst = monthly.loc[monthly['temperature_celsius'].idxmax(), 'month_name']
        st.success(f"Coolest: {best}")
        st.error(f"Hottest: {worst}")
    
    st.markdown("---")
    
    # Air Quality
    st.subheader(f"Air Quality in {country}")
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_aq = country_df.groupby('month')['air_quality_pm2.5'].mean().reset_index()
        monthly_aq['month_name'] = monthly_aq['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
        
        fig = px.line(
            monthly_aq, 
            x='month_name', 
            y='air_quality_pm2.5',
            title=f'Monthly Air Quality (PM2.5) in {country}',
            markers=True
        )
        fig.update_traces(line_color='#98D8C8', line_width=3, marker_size=10)
        fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Hazardous")
        fig.update_layout(height=350, xaxis_title='Month', yaxis_title='PM2.5 (μg/m³)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
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
            title=f'Temperature vs Humidity in {country}',
            labels={'temperature_celsius': 'Temperature (°C)', 
                   'humidity': 'Humidity (%)',
                   'air_quality_pm2.5': 'PM2.5'},
            color_continuous_scale='Viridis'
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        corr = country_df[['temperature_celsius', 'humidity']].corr().iloc[0, 1]
        st.info(f"Correlation: {corr:.2f}")
    
    st.markdown("---")
    
    # Extreme Events
    st.subheader(f"Extreme Events in {country}")
    
    col1, col2, col3 = st.columns(3)
    
    extreme_heat = len(country_df[country_df['temperature_celsius'] > 40])
    col1.metric("Extreme Heat", f"{extreme_heat}", 
               delta=f"{(extreme_heat/len(country_df)*100):.1f}%")
    
    poor_aq = len(country_df[country_df['air_quality_pm2.5'] > 100])
    col2.metric("Poor Air Quality", f"{poor_aq}",
               delta=f"{(poor_aq/len(country_df)*100):.1f}%")
    
    high_wind = len(country_df[country_df['wind_kph'] > 50])
    col3.metric("High Wind", f"{high_wind}",
               delta=f"{(high_wind/len(country_df)*100):.1f}%")
    
    # Locations table
    if country_df['location_name'].nunique() > 1:
        st.markdown("---")
        st.subheader(f"Locations in {country}")
        
        locations = country_df.groupby('location_name').agg({
            'temperature_celsius': 'mean',
            'humidity': 'mean',
            'air_quality_pm2.5': 'mean'
        }).round(1).reset_index()
        locations.columns = ['Location', 'Avg Temp (°C)', 'Avg Humidity (%)', 'Avg PM2.5']
        
        st.dataframe(locations, use_container_width=True, height=300)


def main():
    st.title("ClimateScope Dashboard")
    st.markdown("**Global & Country-Specific Weather Intelligence**")
    
    df = load_data()
    
    # Sidebar
    st.sidebar.header("Analysis Mode")
    mode = st.sidebar.radio(
        "Choose:",
        ["Global Analysis", "Country Analysis"]
    )
    
    st.sidebar.markdown("---")
    
    if mode == "Global Analysis":
        show_global_analysis(df)
    else:
        st.sidebar.subheader("Select Country")
        countries = sorted(df['country'].unique())
        country = st.sidebar.selectbox("Country", countries)
        show_country_analysis(df, country)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>ClimateScope | 107,573 Records | 211 Countries | Author: Sanskriti</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
