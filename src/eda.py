import pandas as pd

# Load CSV
df = pd.read_csv("data/raw/GlobalWeatherRepository.csv")

print("\n===== HEAD =====")
print(df.head())

print("\n===== INFO =====")
print(df.info())

print("\n===== DESCRIBE (NUMERIC) =====")
print(df.describe())

print("\n===== Missing Values =====")
print(df.isnull().sum())

print("\n===== Country Count =====")
print(df['country'].value_counts().head(20))

# Convert last_updated to datetime
df['last_updated'] = pd.to_datetime(df['last_updated'])

print("\n===== Date Range =====")
print("Min:", df['last_updated'].min())
print("Max:", df['last_updated'].max())
