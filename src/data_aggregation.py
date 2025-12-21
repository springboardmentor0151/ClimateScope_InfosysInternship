import pandas as pd

#  Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_weather.csv")

#  Convert last_updated to datetime
df['last_updated'] = pd.to_datetime(df['last_updated'])

#  Select ONLY numeric columns
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

#  Group by month + country but aggregate ONLY numeric columns
monthly = df.groupby(
    [df['last_updated'].dt.to_period('M'), 'country']
)[numeric_cols].mean().reset_index()

# 5. Save
monthly.to_csv("data/processed/monthly_avg.csv", index=False)

print("Monthly aggregation complete! File saved to data/processed/monthly_avg.csv")

