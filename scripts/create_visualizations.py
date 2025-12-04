"""
Visualization Creation Script - Milestone 2
Creates interactive charts and plots for weather data analysis

Author: Naman Mittal
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Paths
PROCESSED_DATA_PATH = Path("data/processed")
OUTPUTS_PATH = Path("data/outputs")
VIZ_PATH = Path("visualizations")
VIZ_PATH.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load processed data"""
    print("Loading data...")
    df = pd.read_csv(PROCESSED_DATA_PATH / "cleaned_weather_data.csv")
    df['last_updated_dt'] = pd.to_datetime(df['last_updated'])
    print(f"Loaded {len(df):,} records\n")
    return df


def create_temperature_distribution(df):
    """Temperature distribution histogram"""
    print("Creating temperature distribution chart...")
    
    fig = px.histogram(
        df, x='temperature_celsius',
        nbins=50,
        title='Global Temperature Distribution',
        labels={'temperature_celsius': 'Temperature (°C)', 'count': 'Frequency'},
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_layout(
        showlegend=False,
        height=500,
        template='plotly_white'
    )
    
    fig.write_html(VIZ_PATH / "temperature_distribution.html")
    print("  Saved: visualizations/temperature_distribution.html")
    return fig


def create_seasonal_trends(df):
    """Monthly temperature trends"""
    print("Creating seasonal trends chart...")
    
    monthly = df.groupby('month').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'precip_mm': 'sum'
    }).reset_index()
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly['month_name'] = monthly['month'].apply(lambda x: months[x-1] if x <= 12 else f'M{x}')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly['month_name'],
        y=monthly['temperature_celsius'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Monthly Temperature Trends',
        xaxis_title='Month',
        yaxis_title='Average Temperature (°C)',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.write_html(VIZ_PATH / "seasonal_trends.html")
    print("  Saved: visualizations/seasonal_trends.html")
    return fig


def create_correlation_heatmap(df):
    """Correlation heatmap"""
    print("Creating correlation heatmap...")
    
    cols = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb', 
            'precip_mm', 'uv_index', 'air_quality_pm2.5']
    
    corr = df[cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title='Weather Variables Correlation Matrix',
        height=600,
        width=700,
        template='plotly_white'
    )
    
    fig.write_html(VIZ_PATH / "correlation_heatmap.html")
    print("  Saved: visualizations/correlation_heatmap.html")
    return fig


def create_regional_comparison(df):
    """Top countries temperature comparison"""
    print("Creating regional comparison chart...")
    
    regional = df.groupby('country').agg({
        'temperature_celsius': 'mean',
        'location_name': 'count'
    }).reset_index()
    
    regional.columns = ['country', 'avg_temp', 'records']
    regional = regional[regional['records'] >= 100]
    
    top_hot = regional.nlargest(15, 'avg_temp')
    top_cold = regional.nsmallest(15, 'avg_temp')
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Hottest Countries', 'Coldest Countries')
    )
    
    fig.add_trace(
        go.Bar(x=top_hot['avg_temp'], y=top_hot['country'], 
               orientation='h', marker_color='#FF6B6B', name='Hot'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=top_cold['avg_temp'], y=top_cold['country'],
               orientation='h', marker_color='#4ECDC4', name='Cold'),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text='Regional Temperature Comparison',
        height=600,
        showlegend=False,
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Avg Temperature (°C)")
    
    fig.write_html(VIZ_PATH / "regional_comparison.html")
    print("  Saved: visualizations/regional_comparison.html")
    return fig


def create_air_quality_scatter(df):
    """Air quality vs temperature scatter plot"""
    print("Creating air quality scatter plot...")
    
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    
    fig = px.scatter(
        sample,
        x='temperature_celsius',
        y='air_quality_pm2.5',
        color='humidity',
        size='wind_kph',
        hover_data=['country', 'location_name'],
        title='Air Quality vs Temperature',
        labels={
            'temperature_celsius': 'Temperature (°C)',
            'air_quality_pm2.5': 'PM2.5 (μg/m³)',
            'humidity': 'Humidity (%)',
            'wind_kph': 'Wind Speed'
        },
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=600,
        template='plotly_white'
    )
    
    fig.write_html(VIZ_PATH / "air_quality_scatter.html")
    print("  Saved: visualizations/air_quality_scatter.html")
    return fig


def create_extreme_events_chart(df):
    """Extreme weather events bar chart"""
    print("Creating extreme events chart...")
    
    extremes = {
        'Extreme Heat\n(>40°C)': len(df[df['temperature_celsius'] > 40]),
        'Extreme Cold\n(<-10°C)': len(df[df['temperature_celsius'] < -10]),
        'Heavy Rain\n(>20mm)': len(df[df['precip_mm'] > 20]),
        'High Wind\n(>50km/h)': len(df[df['wind_kph'] > 50]),
        'Poor Air Quality\n(PM2.5>100)': len(df[df['air_quality_pm2.5'] > 100])
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(extremes.keys()),
            y=list(extremes.values()),
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
            text=list(extremes.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Extreme Weather Events Count',
        xaxis_title='Event Type',
        yaxis_title='Number of Events',
        height=500,
        template='plotly_white'
    )
    
    fig.write_html(VIZ_PATH / "extreme_events.html")
    print("  Saved: visualizations/extreme_events.html")
    return fig


def main():
    """Create all visualizations"""
    print("\n" + "="*60)
    print("CREATING VISUALIZATIONS - MILESTONE 2")
    print("="*60 + "\n")
    
    df = load_data()
    
    create_temperature_distribution(df)
    create_seasonal_trends(df)
    create_correlation_heatmap(df)
    create_regional_comparison(df)
    create_air_quality_scatter(df)
    create_extreme_events_chart(df)
    
    print("\n" + "="*60)
    print("ALL VISUALIZATIONS CREATED!")
    print("="*60)
    print("\nOpen the HTML files in 'visualizations/' folder to view charts")
    print()


if __name__ == "__main__":
    main()
