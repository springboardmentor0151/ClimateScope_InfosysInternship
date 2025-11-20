# Milestone 1: Data Preparation & Initial Analysis

## Dataset Information

### Source
- **Dataset Name**: Global Weather Repository
- **Source**: Kaggle
- **Download Date**: November 20, 2024
- **Original Size**: 107,573 records × 41 columns

## Data Schema

### Key Variables

#### Geographic Information
| Column Name | Data Type | Description | Unit |
|-------------|-----------|-------------|------|
| country | object | Country name | - |
| location_name | object | City/location name | - |
| latitude | float64 | Latitude coordinate | degrees |
| longitude | float64 | Longitude coordinate | degrees |
| timezone | object | Timezone identifier | - |

#### Weather Metrics
| Column Name | Data Type | Description | Unit |
|-------------|-----------|-------------|------|
| temperature_celsius | float64 | Current temperature | °C |
| temperature_fahrenheit | float64 | Current temperature | °F |
| feels_like_celsius | float64 | Feels like temperature | °C |
| humidity | int64 | Relative humidity | % |
| wind_kph | float64 | Wind speed | km/h |
| wind_degree | int64 | Wind direction | degrees |
| pressure_mb | float64 | Atmospheric pressure | mb |
| precip_mm | float64 | Precipitation | mm |
| visibility_km | float64 | Visibility distance | km |
| uv_index | float64 | UV index | - |
| cloud | int64 | Cloud coverage | % |
| condition_text | object | Weather condition description | - |

#### Air Quality Metrics
| Column Name | Data Type | Description | Unit |
|-------------|-----------|-------------|------|
| air_quality_pm2.5 | float64 | PM2.5 concentration | μg/m³ |
| air_quality_pm10 | float64 | PM10 concentration | μg/m³ |
| air_quality_carbon_monoxide | float64 | CO concentration | μg/m³ |
| air_quality_ozone | float64 | O3 concentration | μg/m³ |
| air_quality_nitrogen_dioxide | float64 | NO2 concentration | μg/m³ |
| air_quality_sulphur_dioxide | float64 | SO2 concentration | μg/m³ |
| air_quality_us-epa-index | int64 | US EPA Air Quality Index | 1-6 |

#### Astronomical Data
| Column Name | Data Type | Description | Unit |
|-------------|-----------|-------------|------|
| sunrise | object | Sunrise time | HH:MM AM/PM |
| sunset | object | Sunset time | HH:MM AM/PM |
| moon_phase | object | Moon phase description | - |
| moon_illumination | int64 | Moon illumination | % |

## Data Quality Assessment

### Missing Values
✓ **No missing values detected** in the dataset - all 107,573 records are complete across all 41 columns.

### Anomalies Detected
- **UV Index**: 155 records (0.14%) with UV index > 15 (typically max is 11+)
  - **Action Taken**: Flagged for review but retained as they may represent extreme conditions
- **Wind Speed**: 1 extreme outlier at 2,963 km/h in Bujumbura, Burundi
  - **Action Taken**: Likely data error, flagged for investigation
- **PM10**: Some negative values detected (minimum: -1,848.15)
  - **Action Taken**: Data quality issue noted for future correction

### Data Coverage
- **Time Range**: May 16, 2024 to November 20, 2025 (18 months)
- **Geographic Coverage**: 211 countries, 254 unique locations worldwide
- **Records**: 107,573 total observations
- **Duplicate Rows**: 0 (no duplicates found)

### Top Countries by Data Points
1. Bulgaria: 1,225 records
2. Indonesia: 1,107 records
3. Sudan: 1,104 records
4. Iran: 1,104 records
5. Turkey: 1,103 records

## Data Cleaning Steps

### 1. Data Inspection
- Loaded and inspected 107,573 rows × 41 columns
- Verified data types for all columns
- Checked for missing values (none found)
- Identified duplicate records (none found)

### 2. DateTime Processing
- Converted `last_updated` to datetime format
- Extracted date components: year, month, day, hour
- Added new columns for temporal analysis

### 3. Column Standardization
- Standardized all column names to lowercase
- Replaced spaces with underscores for consistency
- Improved code readability and consistency

### 4. Anomaly Detection
- Checked temperature range (-90°C to 60°C): 0 anomalies
- Checked humidity range (0-100%): 0 anomalies
- Checked UV index (0-15): 155 anomalies flagged

### 5. Data Aggregation
- Created daily country-level averages
- Aggregated 107,573 records into 101,921 daily country summaries
- Calculated mean values for temperature, humidity, wind, pressure, UV, and air quality

## Key Findings

### Weather Patterns
- **Global Average Temperature**: 22.54°C (std: 8.88°C)
- **Temperature Range**: -24.9°C (Ulaanbaatar, Mongolia) to 49.2°C (Kuwait City, Kuwait)
- **Average Humidity**: 64.87%
- **Average Wind Speed**: 13.12 km/h
- **Precipitation**: 33.6% of locations experiencing rain

### Most Common Weather Conditions
1. Partly cloudy: 30.6%
2. Sunny: 30.6%
3. Patchy rain nearby: 8.3%
4. Overcast: 4.9%
5. Clear: 4.4%

### Air Quality Insights
- **52.2%** of locations have "Good" air quality (EPA Index 1)
- **31.9%** have "Moderate" air quality (EPA Index 2)
- **Average PM2.5**: 25.29 μg/m³
- **Average PM10**: 51.29 μg/m³

### Countries with Worst Air Quality (by PM2.5)
1. Chile: 181.88 μg/m³
2. Saudi Arabia: 141.78 μg/m³
3. China: 137.91 μg/m³
4. India: 109.54 μg/m³
5. Kuwait: 99.71 μg/m³

## Results

### Before Cleaning
- **Rows**: 107,573
- **Columns**: 41
- **Missing Values**: 0%
- **Duplicates**: 0

### After Cleaning
- **Rows**: 107,573 (no data loss)
- **Columns**: 47 (added 6 datetime components)
- **Missing Values**: 0%
- **Data Quality**: High quality with minimal anomalies

## Files Generated

### Processed Data
- `data/processed/cleaned_weather_data.csv` - Cleaned dataset with 107,573 rows × 47 columns
- `data/processed/daily_country_averages.csv` - Daily aggregates by country (101,921 rows)

### Analysis Outputs
- `data/outputs/summary_statistics.csv` - Comprehensive statistical summary
- `data/outputs/geographic_coverage.csv` - Geographic distribution analysis
- `data/outputs/data_quality_report.csv` - Data quality metrics

### Scripts
- `scripts/data_cleaning.py` - Data cleaning and preprocessing pipeline
- `scripts/data_analysis.py` - Detailed data analysis and reporting

## Next Steps
1. Proceed to Milestone 2: Data visualization and exploration
2. Create interactive visualizations using Plotly
3. Develop geographic visualizations with Folium
4. Build Streamlit dashboard for interactive exploration
5. Investigate and correct data anomalies (extreme wind speeds, negative PM10 values)

## What I Accomplished
- Downloaded and set up the Global Weather Repository dataset
- Inspected the data structure - found 107,573 records with no missing values
- Cleaned and standardized the data
- Created aggregated datasets for easier analysis
- Generated comprehensive reports on weather patterns and air quality
- Documented all findings and created reusable scripts

---
**Completed by**: Sanskriti  
**Date**: November 2024
