"""
Statistical Analysis Script - Milestone 2
Author: Naman Mittal
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DATA_PATH = Path("data/processed")
OUTPUTS_PATH = Path("data/outputs")
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)


def load_data():
    print("Loading data...")
    df = pd.read_csv(PROCESSED_DATA_PATH / "cleaned_weather_data.csv")
    df['last_updated_dt'] = pd.to_datetime(df['last_updated'])
    print(f"Loaded {len(df):,} records\n")
    return df


def analyze_distributions(df):
    print("="*60)
    print("DISTRIBUTION ANALYSIS")
    print("="*60)
    
    variables = ['temperature_celsius', 'humidity', 'wind_kph', 'precip_mm', 'air_quality_pm2.5']
    distributions = {}
    
    for var in variables:
        stats = df[var].describe()
        print(f"\n{var}:")
        print(f"  Mean: {stats['mean']:.2f}, Median: {stats['50%']:.2f}")
        print(f"  Std: {stats['std']:.2f}, Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
        
        distributions[var] = {
            'mean': stats['mean'], 'median': stats['50%'],
            'std': stats['std'], 'min': stats['min'], 'max': stats['max']
        }
    
    pd.DataFrame(distributions).T.to_csv(OUTPUTS_PATH / "distributions_analysis.csv")
    print(f"\nSaved: data/outputs/distributions_analysis.csv")
    return distributions


def analyze_correlations(df):
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS")
    print("="*60)
    
    cols = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb', 
            'precip_mm', 'uv_index', 'air_quality_pm2.5']
    
    corr_matrix = df[cols].corr()
    
    print("\nStrong Correlations (|r| > 0.5):")
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.5:
                print(f"  {corr_matrix.columns[i]} <-> {corr_matrix.columns[j]}: {corr_val:.3f}")
    
    corr_matrix.to_csv(OUTPUTS_PATH / "correlation_matrix.csv")
    print(f"\nSaved: data/outputs/correlation_matrix.csv")
    return corr_matrix


def analyze_seasonal_patterns(df):
    print("\n" + "="*60)
    print("SEASONAL PATTERNS")
    print("="*60)
    
    monthly = df.groupby('month').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'precip_mm': 'sum'
    }).round(2)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print("\nMonthly Temperature:")
    for m in monthly.index:
        print(f"  {months[m-1]}: {monthly.loc[m, 'temperature_celsius']:.1f}°C")
    
    monthly.to_csv(OUTPUTS_PATH / "seasonal_patterns.csv")
    print(f"\nSaved: data/outputs/seasonal_patterns.csv")
    return monthly


def identify_extreme_events(df):
    print("\n" + "="*60)
    print("EXTREME EVENTS")
    print("="*60)
    
    extremes = {
        'Extreme Heat (>40°C)': len(df[df['temperature_celsius'] > 40]),
        'Extreme Cold (<-10°C)': len(df[df['temperature_celsius'] < -10]),
        'Heavy Rain (>20mm)': len(df[df['precip_mm'] > 20]),
        'High Wind (>50km/h)': len(df[df['wind_kph'] > 50]),
        'Poor Air Quality (PM2.5>100)': len(df[df['air_quality_pm2.5'] > 100])
    }
    
    print("\nEvent Counts:")
    for event, count in extremes.items():
        pct = (count/len(df))*100
        print(f"  {event}: {count:,} ({pct:.2f}%)")
    
    pd.DataFrame(list(extremes.items()), columns=['Event', 'Count']).to_csv(
        OUTPUTS_PATH / "extreme_events.csv", index=False)
    print(f"\nSaved: data/outputs/extreme_events.csv")
    return extremes


def compare_regions(df):
    print("\n" + "="*60)
    print("REGIONAL COMPARISON")
    print("="*60)
    
    regional = df.groupby('country').agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'air_quality_pm2.5': 'mean',
        'location_name': 'count'
    }).round(2)
    
    regional.columns = ['Avg_Temp', 'Avg_Humidity', 'Avg_PM2.5', 'Records']
    regional = regional[regional['Records'] >= 100]
    
    print(f"\nAnalyzed {len(regional)} countries")
    print("\nTop 5 Hottest:")
    for country, row in regional.nlargest(5, 'Avg_Temp').iterrows():
        print(f"  {country}: {row['Avg_Temp']:.1f}°C")
    
    regional.to_csv(OUTPUTS_PATH / "regional_comparison.csv")
    print(f"\nSaved: data/outputs/regional_comparison.csv")
    return regional


def main():
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS - MILESTONE 2")
    print("="*60 + "\n")
    
    df = load_data()
    analyze_distributions(df)
    analyze_correlations(df)
    analyze_seasonal_patterns(df)
    identify_extreme_events(df)
    compare_regions(df)
    
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
