
# Global Weather Repository - Data Schema

## Dataset Overview
- **Source**: Global Weather Repository (Kaggle)
- **Original Rows**: 107,768
- **Cleaned Rows**: 107,768
- **Columns**: 49

## Key Variables

### Location Variables
- country: Country name
- location_name: City/location name
- latitude: Latitude coordinate
- longitude: Longitude coordinate
- timezone: Timezone information

### Temporal Variables
- last_updated: Timestamp of data collection
- date: Date (extracted)
- year: Year (extracted)
- month: Month (extracted)
- day: Day (extracted)
- day_of_week: Day of week name
- hour: Hour (extracted)
- season: Season (Winter/Spring/Summer/Fall)

### Weather Variables
- temperature_celsius: Temperature in Celsius
- temperature_fahrenheit: Temperature in Fahrenheit
- temperature_kelvin: Temperature in Kelvin (derived)
- feels_like_celsius: Feels-like temperature in Celsius
- condition_text: Weather condition description
- humidity: Humidity percentage (0-100)
- pressure_mb: Atmospheric pressure in millibars
- wind_kph: Wind speed in kilometers per hour
- wind_mph: Wind speed in miles per hour
- wind_degree: Wind direction in degrees
- wind_direction: Wind direction (N, S, E, W, etc.)
- precip_mm: Precipitation in millimeters
- precip_in: Precipitation in inches
- cloud: Cloud cover percentage (0-100)
- visibility_km: Visibility in kilometers
- uv_index: UV index (0-15)
- gust_kph: Wind gust speed in kph

### Air Quality Variables
- air_quality_Carbon_Monoxide: CO levels
- air_quality_Ozone: Ozone levels
- air_quality_Nitrogen_dioxide: NO2 levels
- air_quality_Sulphur_dioxide: SO2 levels
- air_quality_PM2.5: PM2.5 particulate matter
- air_quality_PM10: PM10 particulate matter
- air_quality_us-epa-index: US EPA air quality index
- air_quality_gb-defra-index: UK DEFRA air quality index

### Astronomical Variables
- sunrise: Sunrise time
- sunset: Sunset time
- moonrise: Moonrise time
- moonset: Moonset time
- moon_phase: Moon phase description
- moon_illumination: Moon illumination percentage

## Data Quality Issues Addressed
1. Removed duplicate rows
2. Handled missing values using forward fill and median imputation
3. Clipped outliers to reasonable ranges:
   - Temperature: -50°C to 60°C
   - Humidity: 0% to 100%
   - Pressure: 800 mb to 1100 mb
   - Wind speed: 0 kph to 400 kph
   - Precipitation: 0 mm to 1000 mm
   - Cloud cover: 0% to 100%
   - UV index: 0 to 15

## Aggregated Datasets
1. **monthly_weather_data.csv**: Monthly averages per location
2. **daily_weather_data.csv**: Daily averages per location

## Generated: 2025-12-03 10:06:29
