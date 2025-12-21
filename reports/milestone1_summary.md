# Milestone 1: Data Preparation & Initial Analysis  
*(Weeks 1–2)*

## 1. Dataset Overview  
- **Dataset Name:** Global Weather Repository (Kaggle)  
- **File Used:** GlobalWeatherRepository.csv  
- **Rows:** ~107,573  
- **Columns:** 41  
- **Purpose:** Analyze global weather conditions (temperature, humidity, wind, visibility, UV, AQI, sunrise/sunset, etc.)

## 2. Dataset Schema (Important Columns)
- country → string  
- location_name → string  
- latitude, longitude → float  
- timezone → string  
- last_updated → datetime (converted)  
- temperature_celsius → float  
- humidity → int  
- wind_kph, wind_mph → float  
- precip_mm → float  
- visibility_km → float  
- uv_index → float  
- air_quality_* → float  
- sunrise, sunset, moonrise, moonset → string  
- moon_phase → string  
- moon_illumination → int  

## 3. Data Understanding (EDA)
- No missing values found in the dataset.  
- Temperature, humidity, wind, air-quality values present for all rows.  
- Country distribution is imbalanced (some countries 1000+ entries, others < 5).  
- Weather time column = `last_updated` (no `date` column).  
- Sunrise/sunset/moon-phase columns are strings and cannot be aggregated.

## 4. Data Cleaning Steps Performed
- Converted `last_updated` column to datetime.  
- Removed impossible humidity values (<0 or >100).  
- Removed extreme temperature values (< –90°C or > 70°C).  
- Ensured all numeric columns correctly typed as float/int.  
- Removed any rows with corrupted numeric data (if any detected).

## 5. Data Preprocessing
- Selected only numeric columns for aggregation (to avoid string-aggregation errors).  
- Filtered dataset into a cleaned version:
  - **Saved at:** `data/processed/cleaned_weather.csv`

## 6. Monthly Aggregation (Milestone Requirement)
- Grouped data by:
  - Monthly period: `last_updated.dt.to_period('M')`
  - Country
- Calculated monthly averages only for numeric columns (e.g., temperature, humidity, wind, visibility, AQI, UV).  
- **Saved at:** `data/processed/monthly_avg.csv`

## 7. Data Quality Issues Identified
- Dataset has many string fields (timezone, condition_text, sunrise, sunset) that cannot be averaged.  
- Country labels sometimes inconsistent (e.g., “Saudi Arabien”, “Bélgica”).  
- Uneven data distribution across countries.

## 8. Final Output Files (Milestone 1 Deliverables)
- **Cleaned dataset:** `data/processed/cleaned_weather.csv`  
- **Monthly aggregated dataset:** `data/processed/monthly_avg.csv`  

## 9. Success Criteria (Achieved)
✔ Dataset successfully downloaded  
✔ Cleaned (numeric issues fixed, impossible values handled)  
✔ Converted timestamp column  
✔ Monthly aggregated dataset generated  
✔ Ready for Milestone 2 (Exploratory Analysis + Visualizations)

