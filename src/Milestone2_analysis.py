# src/milestone2_analysis.py
import pandas as pd
import numpy as np

print("\n=== MILESTONE 2 ANALYSIS STARTED ===\n")

# -----------------------------------------
# Load processed cleaned weather dataset
# -----------------------------------------
df = pd.read_csv("data/processed/cleaned_weather.csv")

# Convert last_updated → date
df['date'] = pd.to_datetime(df['last_updated'], format='%d-%m-%Y %H:%M', errors='coerce')
df = df.dropna(subset=['date']).sort_values('date')

# Extract month
df['month'] = df['date'].dt.month

# -----------------------------------------
# 1. Region-wise Weather Summary
# -----------------------------------------
print("\n=== REGION-WISE WEATHER SUMMARY ===")
region_summary = df.groupby("country")[['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']].mean()
print(region_summary.head())

# -----------------------------------------
# 2. Monthly Summary
# -----------------------------------------
monthly = df.groupby("month")[['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']].mean().reset_index()
print("\n=== MONTHLY SUMMARY ===")
print(monthly)

# -----------------------------------------
# 3. Detect Extreme Weather Conditions
# -----------------------------------------
extreme = df[
    (df['temperature_celsius'] > 40) |     # heatwave
    (df['precip_mm'] > 100) |              # heavy rainfall
    (df['wind_kph'] > 50)                  # high wind
]

extreme.to_csv("reports/extreme_events.csv", index=False)
print("\nExtreme events saved → reports/extreme_events.csv")

# -----------------------------------------
# 4. Country-wise Average Temperature
# -----------------------------------------
country_avg = df.groupby("country")["temperature_celsius"].mean().reset_index()
country_avg.to_csv("reports/country_avg_temp.csv", index=False)
print("\nCountry Avg Temperature saved → reports/country_avg_temp.csv")

print("\n=== MILESTONE 2 ANALYSIS COMPLETE ===")
