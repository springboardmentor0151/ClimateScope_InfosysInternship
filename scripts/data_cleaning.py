"""
Data Cleaning and Preprocessing Pipeline
Global Weather Repository Dataset Analysis

This script performs comprehensive data cleaning, validation, and preprocessing
on the Global Weather Repository dataset from Kaggle.

Author: Naman
Date: November 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Setup directories for processed data
PROCESSED_DATA_PATH = Path("data/processed")
OUTPUTS_PATH = Path("data/outputs")
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)


def load_data(filename):
    """Load the weather dataset"""
    print(f"Loading data from {filename}...")
    df = pd.read_csv(filename)
    print(f"Loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def inspect_data(df):
   
    print("\n" + "="*60)
    print("DATA INSPECTION AND QUALITY ASSESSMENT")
    print("="*60)
    
    print(f"\nDataset Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    print(f"\nColumn Inventory ({len(df.columns)} total):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col:40s} ({df[col].dtype})")
    
    # Assess data completeness
    print(f"\nData Completeness Assessment:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("  ✓ No missing values detected - 100% data completeness")
    else:
        print("  Missing values detected:")
        for col, count in missing[missing > 0].items():
            print(f"    - {col}: {count} ({count/len(df)*100:.2f}%)")
    
    # Check for duplicates
    dup_count = df.duplicated().sum()
    print(f"\nDuplicate Records: {dup_count}")
    if dup_count == 0:
        print("  ✓ No duplicate records found")
    
    # Geographic coverage
    print(f"\nGeographic Coverage:")
    print(f"  Countries: {df['country'].nunique()}")
    print(f"  Unique Locations: {df['location_name'].nunique()}")
    
    # Temporal coverage
    print(f"\nTemporal Coverage:")
    df['last_updated_dt'] = pd.to_datetime(df['last_updated'])
    print(f"  Start Date: {df['last_updated_dt'].min()}")
    print(f"  End Date: {df['last_updated_dt'].max()}")
    print(f"  Duration: {(df['last_updated_dt'].max() - df['last_updated_dt'].min()).days} days")
    
    return df


def clean_data(df):
    """
    Apply data cleaning and preprocessing transformations.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Raw dataset to clean
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned and preprocessed dataset
    """
    print("\n" + "="*60)
    print("DATA CLEANING AND PREPROCESSING")
    print("="*60)
    
    df_clean = df.copy()
    
    # Step 1: Temporal feature engineering
    print("\n1. Temporal Feature Engineering...")
    df_clean['last_updated_dt'] = pd.to_datetime(df_clean['last_updated'])
    df_clean['date'] = df_clean['last_updated_dt'].dt.date
    df_clean['year'] = df_clean['last_updated_dt'].dt.year
    df_clean['month'] = df_clean['last_updated_dt'].dt.month
    df_clean['day'] = df_clean['last_updated_dt'].dt.day
    df_clean['hour'] = df_clean['last_updated_dt'].dt.hour
    print("   ✓ Extracted temporal components: date, year, month, day, hour")
    
    # Step 2: Duplicate removal
    print("\n2. Duplicate Record Removal...")
    before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    after = len(df_clean)
    if before > after:
        print(f"   ✓ Removed {before - after:,} duplicate records ({(before-after)/before*100:.2f}%)")
    else:
        print(f"   ✓ No duplicate records detected")
    
    # Step 3: Column name standardization
    print("\n3. Column Name Standardization...")
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    print("   ✓ Standardized column names to lowercase with underscores")
    
    # Step 4: Data validation and anomaly detection
    print("\n4. Data Validation and Anomaly Detection...")
    
    # Temperature validation (typical range: -90°C to 60°C)
    temp_anomalies = (df_clean['temperature_celsius'] < -90) | (df_clean['temperature_celsius'] > 60)
    print(f"   Temperature anomalies: {temp_anomalies.sum()} records")
    
    # Humidity validation (valid range: 0-100%)
    humidity_anomalies = (df_clean['humidity'] < 0) | (df_clean['humidity'] > 100)
    print(f"   Humidity anomalies: {humidity_anomalies.sum()} records")
    
    # UV index validation (typical range: 0-15)
    uv_anomalies = (df_clean['uv_index'] < 0) | (df_clean['uv_index'] > 15)
    print(f"   UV index anomalies: {uv_anomalies.sum()} records ({uv_anomalies.sum()/len(df_clean)*100:.2f}%)")
    
    return df_clean


def create_aggregated_data(df):
    """
    Create aggregated datasets for time-series analysis.
    
    Aggregates weather and air quality metrics by country and date,
    calculating daily averages for key variables.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Cleaned dataset
        
    Returns:
    --------
    pandas.DataFrame
        Daily aggregated data by country
    """
    print("\n" + "="*60)
    print("DATA AGGREGATION")
    print("="*60)
    
    print("\n1. Creating Daily Country-Level Aggregates...")
    daily_country = df.groupby(['country', 'date']).agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'wind_kph': 'mean',
        'pressure_mb': 'mean',
        'precip_mm': 'sum',
        'uv_index': 'mean',
        'air_quality_pm2.5': 'mean',
        'air_quality_pm10': 'mean'
    }).reset_index()
    
    print(f"   ✓ Generated {daily_country.shape[0]:,} daily country records")
    print(f"   ✓ Aggregation reduced dataset by {(1 - daily_country.shape[0]/len(df))*100:.1f}%")
    
    # Save aggregated data
    output_path = PROCESSED_DATA_PATH / "daily_country_averages.csv"
    daily_country.to_csv(output_path, index=False)
    print(f"   ✓ Saved to: {output_path}")
    
    return daily_country


def generate_summary_statistics(df):
    """
    Generate comprehensive statistical summary of the dataset.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Cleaned dataset
        
    Returns:
    --------
    pandas.DataFrame
        Statistical summary of numeric columns
    """
    print("\n" + "="*60)
    print("STATISTICAL SUMMARY GENERATION")
    print("="*60)
    
    # Generate descriptive statistics for numeric columns
    numeric_summary = df.describe()
    print("\nDescriptive Statistics (Numeric Variables):")
    print(numeric_summary)
    
    # Save statistical summary
    output_path = OUTPUTS_PATH / "summary_statistics.csv"
    numeric_summary.to_csv(output_path)
    print(f"\n✓ Statistical summary saved to: {output_path}")
    
    # Categorical variable analysis
    print("\nTop 10 Countries by Record Count:")
    country_dist = df['country'].value_counts().head(10)
    for country, count in country_dist.items():
        print(f"  {country}: {count:,} records")
    
    print("\nWeather Condition Distribution (Top 10):")
    condition_dist = df['condition_text'].value_counts().head(10)
    for condition, count in condition_dist.items():
        print(f"  {condition}: {count:,} records ({count/len(df)*100:.1f}%)")
    
    return numeric_summary


def save_cleaned_data(df, filename="cleaned_weather_data.csv"):
    """Save the cleaned data"""
    output_path = PROCESSED_DATA_PATH / filename
    df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to: {output_path}")
    print(f"Final size: {df.shape[0]} rows × {df.shape[1]} columns")


def main():
    """
    Execute the complete data cleaning and preprocessing pipeline.
    
    Pipeline Steps:
    1. Load raw dataset
    2. Inspect data quality and structure
    3. Clean and preprocess data
    4. Generate statistical summaries
    5. Create aggregated datasets
    6. Save processed outputs
    """
    print("\n" + "="*60)
    print("DATA CLEANING AND PREPROCESSING PIPELINE")
    print("Milestone 1: Data Preparation & Initial Analysis")
    print("="*60)
    print(f"Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Pipeline execution
    df = load_data("GlobalWeatherRepository.csv")
    df = inspect_data(df)
    df_cleaned = clean_data(df)
    summary = generate_summary_statistics(df_cleaned)
    daily_agg = create_aggregated_data(df_cleaned)
    save_cleaned_data(df_cleaned)
    
    # Pipeline completion summary
    print("\n" + "="*60)
    print("PIPELINE EXECUTION COMPLETE")
    print("="*60)
    print(f"\nData Transformation Summary:")
    print(f"  Original Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  Cleaned Dataset: {df_cleaned.shape[0]:,} rows × {df_cleaned.shape[1]} columns")
    print(f"  Features Added: {df_cleaned.shape[1] - df.shape[1]} new columns")
    
    print(f"\nGenerated Outputs:")
    print(f"  1. data/processed/cleaned_weather_data.csv")
    print(f"  2. data/processed/daily_country_averages.csv")
    print(f"  3. data/outputs/summary_statistics.csv")
    
    print(f"\nExecution Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
