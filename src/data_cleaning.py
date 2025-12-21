import pandas as pd

df = pd.read_csv("data/raw/GlobalWeatherRepository.csv")

# Convert last_updated to datetime
df['last_updated'] = pd.to_datetime(df['last_updated'])

# Remove impossible humidity values
df = df[(df['humidity'] >= 0) & (df['humidity'] <= 100)]

# Remove impossible temperatures
df = df[(df['temperature_celsius'] > -90) & (df['temperature_celsius'] < 70)]

# Save cleaned file
df.to_csv("data/processed/cleaned_weather.csv", index=False)
print("Saved cleaned_weather.csv")
