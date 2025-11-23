import pandas as pd
df = pd.read_csv("data/GlobalWeatherRepository.csv")
print(df.head())
import pandas as pd

def clean_dataset():

    # Load raw dataset (change path if your CSV name is different)
    df = pd.read_csv("data/GlobalWeatherRepository.csv")

    # -------------------------
    # Basic checks
    # -------------------------
    print(df.head())
    print(df.info())
    print(df.describe())

    # -------------------------
    # Missing value analysis
    # -------------------------
    missing_counts = df.isnull().sum().sort_values(ascending=False)
    print("Top missing values:\n", missing_counts.head(20))

    # Drop columns with more than 80% missing values
    thresh = len(df) * 0.2
    df = df.dropna(axis=1, thresh=thresh)

    # -------------------------
    # Fill numeric missing values with median
    # -------------------------
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())

    # -------------------------
    # Fill categorical missing values with mode
    # -------------------------
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # -------------------------
    # Sorting and filling
    # -------------------------
    df = df.sort_values(["location_name", "last_updated"])
    df = df.ffill()
    df = df.bfill()

    # -------------------------
    # Type conversions
    # -------------------------
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    df["pressure_mb"] = pd.to_numeric(df["pressure_mb"], errors="coerce")

    df["condition_text"] = df["condition_text"].str.strip().str.lower()
    df["location_name"] = df["location_name"].astype("category")

    # -------------------------
    # Remove duplicate rows
    # -------------------------
    df = df.drop_duplicates(subset=["location_name", "last_updated"], keep="last")

    # -------------------------
    # Wind direction mapping
    # -------------------------
    wind_direction_map = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
    }

    if "wind_direction" in df.columns:
        df["wind_direction_degrees"] = df["wind_direction"].map(wind_direction_map)

    # Reconvert last_updated (safe)
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

    # -------------------------
    # Extract time components
    # -------------------------
    df["year"] = df["last_updated"].dt.year
    df["month"] = df["last_updated"].dt.month
    df["day"] = df["last_updated"].dt.day
    df["hour"] = df["last_updated"].dt.hour

    # -------------------------
    # Drop unnecessary columns
    # -------------------------
    drop_cols = [
        "temperature_fahrenheit",
        "feels_like_fahrenheit",
        "precip_in",
        "pressure_in",
        "visibility_miles"
    ]

    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # -------------------------
    # Negative value handling example
    # -------------------------
    if "precip_mm" in df.columns:
        df.loc[df["precip_mm"] < 0, "precip_mm"] = 0

    # -------------------------
    # Set index
    # -------------------------
    df = df.set_index(["location_name", "last_updated"])
    df = df.sort_index()

    # -------------------------
    # Save cleaned dataset
    # -------------------------
    df.to_csv("data/GlobalWeatherRepository.csv")

    print("\nCleaning complete! File saved as: data/cleaned_weather.csv")


if __name__ == "__main__":
    clean_dataset()