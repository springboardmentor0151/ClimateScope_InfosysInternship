"""
Comprehensive Data Analysis Script
Global Weather Repository Dataset

This script performs detailed exploratory data analysis on the cleaned
weather dataset, including geographic coverage, weather patterns, air quality,
and extreme weather event identification.

Author: Sanskriti
Date: November 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DATA_PATH = Path("data/processed")
OUTPUTS_PATH = Path("data/outputs")
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)


def load_cleaned_data(filename="cleaned_weather_data.csv"):
    """Load the cleaned data"""
    filepath = PROCESSED_DATA_PATH / filename
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns")
    return df


def analyze_geographic_coverage(df):
    """
    Analyze geographic distribution and coverage of the dataset.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Cleaned weather dataset
    """
    print("\n" + "="*60)
    print("GEOGRAPHIC COVERAGE ANALYSIS")
    print("="*60)
    
    print(f"\nGlobal Coverage:")
    print(f"  Total Countries: {df['country'].nunique()}")
    print(f"  Total Locations: {df['location_name'].nunique()}")
    print(f"  Average Locations per Country: {df['location_name'].nunique() / df['country'].nunique():.1f}")
    
    # Country-level location distribution
    print("\nTop 15 Countries by Location Count:")
    country_counts = df.groupby('country')['location_name'].nunique().sort_values(ascending=False).head(15)
    for rank, (country, count) in enumerate(country_counts.items(), 1):
        print(f"  {rank:2d}. {country:40s} {count} locations")
    
    # Generate geographic summary report
    geo_summary = df.groupby('country').agg({
        'location_name': 'nunique',
        'latitude': ['min', 'max'],
        'longitude': ['min', 'max']
    }).round(2)
    
    output_path = OUTPUTS_PATH / "geographic_coverage.csv"
    geo_summary.to_csv(output_path)
    print(f"\n✓ Geographic coverage report saved to: {output_path}")


def analyze_weather_patterns(df):
    """Analyze weather patterns and distributions"""
    print("\n" + "="*60)
    print("WEATHER PATTERNS ANALYSIS")
    print("="*60)
    
    print("\nTemperature Statistics (Celsius):")
    print(f"  Global Average: {df['temperature_celsius'].mean():.2f}°C")
    print(f"  Minimum: {df['temperature_celsius'].min():.2f}°C")
    print(f"  Maximum: {df['temperature_celsius'].max():.2f}°C")
    print(f"  Std Dev: {df['temperature_celsius'].std():.2f}°C")
    
    print("\nHumidity Statistics:")
    print(f"  Average: {df['humidity'].mean():.2f}%")
    print(f"  Range: {df['humidity'].min():.0f}% - {df['humidity'].max():.0f}%")
    
    print("\nWind Speed Statistics (km/h):")
    print(f"  Average: {df['wind_kph'].mean():.2f} km/h")
    print(f"  Maximum: {df['wind_kph'].max():.2f} km/h")
    
    print("\nPrecipitation Statistics (mm):")
    print(f"  Average: {df['precip_mm'].mean():.2f} mm")
    print(f"  Maximum: {df['precip_mm'].max():.2f} mm")
    print(f"  Locations with rain: {(df['precip_mm'] > 0).sum()} ({(df['precip_mm'] > 0).sum()/len(df)*100:.1f}%)")
    
    print("\nMost Common Weather Conditions:")
    conditions = df['condition_text'].value_counts().head(10)
    for condition, count in conditions.items():
        print(f"  {condition}: {count} ({count/len(df)*100:.1f}%)")


def analyze_air_quality(df):
    """Analyze air quality metrics"""
    print("\n" + "="*60)
    print("AIR QUALITY ANALYSIS")
    print("="*60)
    
    print("\nPM2.5 Statistics (μg/m³):")
    print(f"  Average: {df['air_quality_pm2.5'].mean():.2f}")
    print(f"  Range: {df['air_quality_pm2.5'].min():.2f} - {df['air_quality_pm2.5'].max():.2f}")
    
    print("\nPM10 Statistics (μg/m³):")
    print(f"  Average: {df['air_quality_pm10'].mean():.2f}")
    print(f"  Range: {df['air_quality_pm10'].min():.2f} - {df['air_quality_pm10'].max():.2f}")
    
    print("\nUS EPA Air Quality Index Distribution:")
    epa_dist = df['air_quality_us-epa-index'].value_counts().sort_index()
    epa_labels = {1: "Good", 2: "Moderate", 3: "Unhealthy for Sensitive", 
                  4: "Unhealthy", 5: "Very Unhealthy", 6: "Hazardous"}
    for idx, count in epa_dist.items():
        label = epa_labels.get(idx, f"Index {idx}")
        print(f"  {label}: {count} ({count/len(df)*100:.1f}%)")
    
    # Countries with worst air quality
    print("\nTop 10 Countries by Average PM2.5:")
    worst_aq = df.groupby('country')['air_quality_pm2.5'].mean().sort_values(ascending=False).head(10)
    for country, pm25 in worst_aq.items():
        print(f"  {country}: {pm25:.2f} μg/m³")


def analyze_extreme_weather(df):
    """Identify extreme weather conditions"""
    print("\n" + "="*60)
    print("EXTREME WEATHER CONDITIONS")
    print("="*60)
    
    print("\nHottest Locations:")
    hottest = df.nlargest(5, 'temperature_celsius')[['country', 'location_name', 'temperature_celsius']]
    for _, row in hottest.iterrows():
        print(f"  {row['location_name']}, {row['country']}: {row['temperature_celsius']:.1f}°C")
    
    print("\nColdest Locations:")
    coldest = df.nsmallest(5, 'temperature_celsius')[['country', 'location_name', 'temperature_celsius']]
    for _, row in coldest.iterrows():
        print(f"  {row['location_name']}, {row['country']}: {row['temperature_celsius']:.1f}°C")
    
    print("\nHighest Wind Speeds:")
    windiest = df.nlargest(5, 'wind_kph')[['country', 'location_name', 'wind_kph']]
    for _, row in windiest.iterrows():
        print(f"  {row['location_name']}, {row['country']}: {row['wind_kph']:.1f} km/h")
    
    print("\nHighest Precipitation:")
    rainiest = df.nlargest(5, 'precip_mm')[['country', 'location_name', 'precip_mm']]
    for _, row in rainiest.iterrows():
        print(f"  {row['location_name']}, {row['country']}: {row['precip_mm']:.1f} mm")


def generate_data_quality_report(df):
    """Generate comprehensive data quality report"""
    print("\n" + "="*60)
    print("DATA QUALITY REPORT")
    print("="*60)
    
    quality_metrics = {
        "Total Records": len(df),
        "Total Columns": len(df.columns),
        "Duplicate Rows": df.duplicated().sum(),
        "Missing Values": df.isnull().sum().sum(),
        "Memory Usage (MB)": df.memory_usage(deep=True).sum() / 1024**2
    }
    
    print("\nQuality Metrics:")
    for metric, value in quality_metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.2f}")
        else:
            print(f"  {metric}: {value}")
    
    print("\nData Type Distribution:")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  {dtype}: {count} columns")
    
    # Save quality report
    quality_df = pd.DataFrame([quality_metrics])
    quality_df.to_csv(OUTPUTS_PATH / "data_quality_report.csv", index=False)
    print(f"\n✓ Saved to: data/outputs/data_quality_report.csv")


def main():
    """
    Execute comprehensive exploratory data analysis.
    
    Analysis Components:
    1. Geographic coverage assessment
    2. Weather pattern analysis
    3. Air quality evaluation
    4. Extreme weather identification
    5. Data quality reporting
    """
    print("\n" + "="*60)
    print("EXPLORATORY DATA ANALYSIS")
    print("Global Weather Repository Dataset")
    print("="*60)
    
    # Load cleaned dataset
    df = load_cleaned_data()
    
    # Execute analysis modules
    analyze_geographic_coverage(df)
    analyze_weather_patterns(df)
    analyze_air_quality(df)
    analyze_extreme_weather(df)
    generate_data_quality_report(df)
    
    # Analysis completion
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nGenerated Reports:")
    print("  1. data/outputs/geographic_coverage.csv")
    print("  2. data/outputs/data_quality_report.csv")


if __name__ == "__main__":
    main()
