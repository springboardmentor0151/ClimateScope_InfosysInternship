# ClimateScope  
## End-to-End Climate Data Analytics & Interactive Dashboard Project

---

# Milestone 1: Data Preparation & Initial Analysis  
*(Weeks 1–2)*

## 1. Dataset Overview  
- **Dataset Name:** Global Weather Repository (Kaggle)  
- **File Used:** GlobalWeatherRepository.csv  
- **Rows:** ~107,573  
- **Columns:** 41  
- **Purpose:** To analyze global weather conditions including temperature, humidity, wind, precipitation, air quality, UV index, and astronomical parameters.

---

## 2. Dataset Schema (Key Columns)
- country  
- location_name  
- latitude, longitude  
- timezone  
- last_updated  
- temperature_celsius  
- humidity  
- wind_kph, wind_mph  
- precip_mm  
- visibility_km  
- uv_index  
- air_quality_*  
- sunrise, sunset, moonrise, moonset  
- moon_phase, moon_illumination  

---

## 3. Data Understanding (EDA)
- Dataset contains structured global weather records.
- Time information available only through `last_updated`.
- Country-wise distribution is imbalanced.
- Several string-based columns are non-aggregatable.
- Weather and air-quality data are consistently populated.

---

## 4. Data Cleaning Steps
- Converted `last_updated` to datetime format.
- Removed invalid humidity values (<0 or >100).
- Removed extreme temperature outliers (< -90°C or > 70°C).
- Ensured numeric columns were correctly typed.
- Removed corrupted or invalid rows where detected.

---

## 5. Data Preprocessing
- Selected numeric columns for aggregation.
- Created a cleaned dataset for analysis.
- **Saved File:** `data/processed/cleaned_weather.csv`

---

## 6. Monthly Aggregation
- Grouped data by:
  - Country
  - Monthly period (`last_updated.dt.to_period('M')`)
- Calculated monthly averages for numeric variables.
- **Saved File:** `data/processed/monthly_avg.csv`

---

## 7. Data Quality Issues Identified
- Presence of many string-based fields.
- Inconsistent country naming.
- Uneven country-level data distribution.

---

## 8. Milestone 1 Deliverables
- Cleaned dataset
- Monthly aggregated dataset
- Dataset ready for visualization and analysis

---

## 9. Milestone 1 Status  
**Completed Successfully**

---

# Milestone 2: Exploratory Analysis & Basic Dashboard  
*(Weeks 3–4)*

## 1. Objective  
To perform exploratory analysis and develop a **basic visualization dashboard** using Streamlit.

---

## 2. Analysis Performed
- Country-wise average temperature analysis
- Monthly climate trends
- Identification of extreme weather conditions
- Summary statistics for key weather variables

---

## 3. Visualizations Implemented
- Line charts for temperature trends
- Bar charts for country comparisons
- Scatter plots for variable relationships
- Basic tables for extreme events

---

## 4. Dashboard Development
- Framework: Streamlit
- IDE: VS Code
- Single-page dashboard
- Static visualizations (no filters)

---

## 5. Milestone 2 Deliverables
- Analysis scripts
- Initial Streamlit dashboard
- Static plots and summaries

---

## 6. Milestone 2 Status  
**Completed Successfully**

---

# Milestone 3: Interactive Dashboard & Advanced Visual Analysis  
*(Weeks 5–6)*

## 1. Objective  
To enhance the dashboard with **interactive filters, multiple visualizations, and improved UI/UX**.

---

## 2. Dataset Used
- Cleaned dataset from Milestone 1  
- **File:** `data/processed/cleaned_weather.csv`

---

## 3. Technologies Used
- Python  
- Streamlit  
- Plotly  
- Matplotlib & Seaborn  

---

## 4. Sidebar Filters Implemented
- Climate zone selection
- Seasonal filter
- Temperature range slider
- Extreme event toggle
- CSV export option

---

## 5. Visualizations Implemented
- Global temperature distribution map
- Histograms and box plots
- Correlation heatmap
- Country-wise comparisons
- Extreme events frequency chart

---

## 6. Interactivity Features
- Dynamic filtering
- Hover tooltips
- Zoom and pan support
- Responsive layout

---

## 7. Milestone 3 Deliverables
- Interactive Streamlit dashboard
- Multiple visualization tabs
- Improved UI/UX

---

## 8. Milestone 3 Status  
**Completed Successfully**

---

# Milestone 4: Advanced Interactive Dashboard & Final Analytics  
*(Weeks 7–8)*

## 1. Objective  
To transform the dashboard into a **near-production-ready climate analytics platform** with advanced metrics, trends, and documentation.

---

## 2. Advanced Climate Metrics Added
- Heat Index
- Wind Chill
- 7-Day Moving Average
- Monthly Aggregation Toggle

---

## 3. Advanced Visualizations
- Area chart for climate trends
- Violin plot for seasonal distribution
- Monthly extreme events trend
- Extreme events tables

---

## 4. Dashboard Structure
- Executive Dashboard (KPIs)
- Statistical Analysis
- Climate Trends
- Extreme Events
- Help & User Guide

---

## 5. Interactivity & UX Enhancements
- Time aggregation selector
- Real-time updates
- Dark theme UI
- Clear layout and navigation
- Exportable reports

---

## 6. Documentation & Reporting
- Integrated Help & User Guide
- Downloadable Milestone-4 summary
- Final project documentation

---

## 7. Milestone 4 Deliverables
- Fully interactive Streamlit dashboard
- Advanced analytics implementation
- User documentation
- Final project report

---

## 8. Final Project Status  
**Milestone 4 – Completed Successfully**

---

# Final Conclusion

The ClimateScope project successfully delivers a **complete end-to-end climate analytics solution**, progressing from raw data preparation to a fully interactive and advanced dashboard. The system enables deep exploration of global climate patterns, extreme weather behavior, and temporal trends through intuitive visualizations and interactivity. The project is academically robust, technically sound, and ready for final evaluation.

---

### **Overall Project Status:**  
**Successfully Completed (Milestones 1–4)**  
