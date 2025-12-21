📄 Milestone 2 Report — ClimateScope Project
Country-Based Weather Analysis Dashboard (Streamlit)
## 1. Objective of Milestone 2

The purpose of Milestone 2 was to:

Analyze the weather conditions of different countries

Identify any extreme weather patterns

Perform statistical analysis on cleaned data

Create a basic dashboard without any filters

Use Streamlit to visualize the data

Use only the cleaned dataset generated in Milestone 1

## 2. Dataset Description

The dataset is a single-day snapshot of global weather collected using API-based data.

Important Columns in the Dataset:
Column	Description
country	Country name
location_name	City/Region name
last_updated	Date & time of the weather record
temperature_celsius	Temperature in Celsius
humidity	Humidity percentage
precip_mm	Rainfall in millimeters
wind_kph	Wind speed in km/h



## 3. Data Preparation

The cleaned dataset from Milestone 1 was used.

Additional preparation in Milestone 2:

Converted last_updated column into a valid datetime format

Removed rows with invalid timestamps

Extracted month value (only for formatting)

## 4. Analysis Performed
### 4.1 Temperature Analysis

Identified the hottest country

Identified the coldest country

Created a bar chart of the top 20 hottest countries

### 4.2 Rainfall Analysis

Ranked countries based on rainfall

Visualized rainfall distribution across countries

### 4.3 Humidity Analysis

Found the most humid country

Plotted Temperature vs Humidity to observe relationships

### 4.4 Extreme Weather Detection

Extreme weather was detected using the following rules:

Condition	Rule
Heatwave	Temperature > 40°C
Heavy Rainfall	precip_mm > 100 mm
High Wind	wind_kph > 50 km/h

Detected events were exported to:
📌 reports/extreme_events.csv

## 5. Dashboard (Streamlit)

A modern, clean, and filter-free dashboard was created using Streamlit.

The dashboard includes:
⭐ Metric Cards

Max Temperature (with country)

Min Temperature (with country)

Max Humidity (with country)

Max Rainfall (with country)

⭐ Visualizations

Bar chart of temperature by country

Bar chart of rainfall by country

Temperature vs Humidity scatter plot

Table of extreme weather events

Statistical summary table

⭐ Design Features

Dark theme

Gradient title

Custom CSS styling

Attractive visualization colors

Premium layout

## 6. Key Insights

Some countries show extremely high temperatures (above 45°C).

A few countries have rainfall above 40 mm within the same day.

Humidity varies significantly between tropical and dry regions.

Temperature vs Humidity shows clear climate patterns.

No extreme events beyond basic thresholds for many countries.

## 7. Files Generated

streamlit_app.py — Final dashboard

reports/extreme_events.csv — Extreme weather extracted

milestone2_summary.md — This report

## 8. Conclusion

Milestone 2 was successfully completed.
The following were achieved:

✔ Cleaned dataset used
✔ Country-based weather analysis performed
✔ Extreme weather detected
✔ Professional, modern Streamlit dashboard created
✔ No filters included (requirement satisfied)