# =============================================================================
# COMPLETE WEATHER DATA CLEANING & PREPARATION - BASIC VERSION
# =============================================================================
import pandas as pd
import numpy as np
import os
import sys

print("🚀 STARTING WEATHER DATA CLEANING PROCESS...")
print("=" * 70)

# =============================================================================
# CHECK AND INSTALL REQUIRED LIBRARIES
# =============================================================================
def check_libraries():
    """Check if required libraries are installed"""
    required_libs = ['pandas', 'numpy']
    missing_libs = []
    
    for lib in required_libs:
        try:
            __import__(lib)
            print(f"✅ {lib} is installed")
        except ImportError:
            missing_libs.append(lib)
    
    if missing_libs:
        print(f"❌ Missing libraries: {missing_libs}")
        print("Please run: pip install " + " ".join(missing_libs))
        return False
    return True

if not check_libraries():
    sys.exit(1)

# =============================================================================
# STEP 1: LOAD THE DATA
# =============================================================================
try:
    df = pd.read_csv(r"C:\Users\HP\Downloads\infosys_SpringBoard\GlobalWeatherRepository.csv")
    print("✅ Original dataset loaded successfully!")
    print(f"📊 Original shape: {df.shape}")
except FileNotFoundError:
    print("❌ Error: File not found. Please check the file path.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading file: {e}")
    sys.exit(1)

# =============================================================================
# STEP 2: COMPREHENSIVE DATA INSPECTION
# =============================================================================
print("\n" + "=" * 70)
print("DATA INSPECTION & QUALITY ASSESSMENT")
print("=" * 70)

print("\n📋 FIRST 3 ROWS OF DATA:")
print(df.head(3))

print(f"\n🏷️  DATASET INFO:")
print(f"   - Total Rows: {df.shape[0]:,}")
print(f"   - Total Columns: {df.shape[1]}")
print(f"   - Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print("\n📊 DATA TYPES SUMMARY:")
print(df.dtypes.value_counts())

print("\n❌ MISSING VALUES ANALYSIS:")
missing_data = df.isnull().sum()
missing_percent = (missing_data / len(df)) * 100

missing_df = pd.DataFrame({
    'Missing_Count': missing_data,
    'Missing_Percentage': missing_percent
}).sort_values('Missing_Count', ascending=False)

# Show only columns with missing values
missing_with_values = missing_df[missing_df['Missing_Count'] > 0]
if len(missing_with_values) > 0:
    print("Columns with missing values:")
    for col in missing_with_values.index:
        count = missing_with_values.loc[col, 'Missing_Count']
        percent = missing_with_values.loc[col, 'Missing_Percentage']
        print(f"   - {col}: {count} ({percent:.2f}%)")
else:
    print("   ✅ No missing values found!")

print(f"\n🔍 DUPLICATE ROWS: {df.duplicated().sum()}")

# =============================================================================
# STEP 3: DATA CLEANING PROCESS
# =============================================================================
print("\n" + "=" * 70)
print("DATA CLEANING IN PROGRESS...")
print("=" * 70)

# Store original statistics for reporting
original_rows, original_cols = df.shape
original_missing = df.isnull().sum().sum()

# 3.1 Handle Missing Values
print("\n1. 🧹 HANDLING MISSING VALUES:")

cleaning_log = []
for col in df.columns:
    if df[col].isnull().sum() > 0:
        missing_count = df[col].isnull().sum()
        
        # For numerical columns
        if df[col].dtype in ['float64', 'int64']:
            if 'air_quality' in col:
                # Air quality data - fill with 0 (assuming no pollution)
                df[col].fillna(0, inplace=True)
                cleaning_log.append(f"Air Quality '{col}': Filled {missing_count} with 0")
            else:
                # Other numerical - fill with median
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                cleaning_log.append(f"Numerical '{col}': Filled {missing_count} with median ({median_val:.2f})")
        
        # For categorical columns
        elif df[col].dtype == 'object':
            if not df[col].mode().empty:
                mode_val = df[col].mode()[0]
            else:
                mode_val = 'Unknown'
            df[col].fillna(mode_val, inplace=True)
            cleaning_log.append(f"Categorical '{col}': Filled {missing_count} with '{mode_val}'")

# Print cleaning log
for log_entry in cleaning_log:
    print(f"   ✅ {log_entry}")

if not cleaning_log:
    print("   ✅ No missing values to handle")

# 3.2 Remove Duplicates
print(f"\n2. 🔍 REMOVING DUPLICATES:")
duplicates = df.duplicated().sum()
if duplicates > 0:
    df.drop_duplicates(inplace=True)
    print(f"   ✅ Removed {duplicates} duplicate rows")
else:
    print("   ✅ No duplicates found")

# 3.3 Convert Data Types
print(f"\n3. 🔄 CONVERTING DATA TYPES:")

# Convert datetime columns
datetime_columns = ['last_updated', 'sunrise', 'sunset', 'moonrise', 'moonset']
converted_count = 0
for col in datetime_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        converted_count += 1

if converted_count > 0:
    print(f"   ✅ Converted {converted_count} columns to datetime")
else:
    print("   ✅ No datetime columns to convert")

# =============================================================================
# STEP 4: FEATURE ENGINEERING
# =============================================================================
print(f"\n" + "=" * 70)
print("FEATURE ENGINEERING")
print("=" * 70)

# 4.1 Create time-based features (if datetime column exists)
if 'last_updated' in df.columns and df['last_updated'].dtype == 'datetime64[ns]':
    df['hour'] = df['last_updated'].dt.hour
    df['day_of_week'] = df['last_updated'].dt.day_name()
    df['month'] = df['last_updated'].dt.month
    df['season'] = df['month'].apply(lambda x: 'Winter' if x in [12, 1, 2] else 
                                              'Spring' if x in [3, 4, 5] else 
                                              'Summer' if x in [6, 7, 8] else 'Autumn')
    print("   ✅ Created time-based features: hour, day_of_week, month, season")

# 4.2 Create climate zones based on latitude
if 'latitude' in df.columns:
    df['climate_zone'] = pd.cut(df['latitude'], 
                               bins=[-90, -23.5, 23.5, 90], 
                               labels=['Southern Temperate', 'Tropical', 'Northern Temperate'])
    print("   ✅ Created climate zones based on latitude")

# 4.3 Create comfort index (simplified)
if all(col in df.columns for col in ['temperature_celsius', 'humidity', 'wind_kph']):
    df['comfort_index'] = (df['temperature_celsius'] / 30 + 
                          (100 - df['humidity']) / 100 + 
                          df['wind_kph'] / 50)
    print("   ✅ Created comfort index")

# =============================================================================
# STEP 5: DATA QUALITY REPORT
# =============================================================================
print(f"\n" + "=" * 70)
print("DATA QUALITY REPORT")
print("=" * 70)

print(f"📈 DATA CLEANING SUMMARY:")
print(f"   • Original dataset: {original_rows:,} rows, {original_cols} columns")
print(f"   • Final dataset:    {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"   • Rows removed:     {original_rows - df.shape[0]:,}")
print(f"   • Columns added:    {df.shape[1] - original_cols}")
print(f"   • Missing values:   {original_missing} → {df.isnull().sum().sum()}")

print(f"\n📊 FINAL DATA OVERVIEW:")
if 'country' in df.columns:
    print(f"   • Countries: {df['country'].nunique()}")
if 'location_name' in df.columns:
    print(f"   • Locations: {df['location_name'].nunique()}")
if 'last_updated' in df.columns:
    print(f"   • Date range: {df['last_updated'].min()} to {df['last_updated'].max()}")
if 'temperature_celsius' in df.columns:
    print(f"   • Temperature range: {df['temperature_celsius'].min():.1f}°C to {df['temperature_celsius'].max():.1f}°C")

print(f"\n🏷️  COLUMN CATEGORIES:")
numerical_count = len(df.select_dtypes(include=[np.number]).columns)
categorical_count = len(df.select_dtypes(include=['object']).columns)
datetime_count = len(df.select_dtypes(include=['datetime64']).columns)

print(f"   • Numerical columns:  {numerical_count}")
print(f"   • Categorical columns: {categorical_count}")
print(f"   • Datetime columns:    {datetime_count}")

# =============================================================================
# STEP 6: SAVE CLEANED DATA
# =============================================================================
print(f"\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

# Save main cleaned dataset
output_file = r"C:\Users\HP\Downloads\infosys_SpringBoard\weather_data_cleaned.csv"
df.to_csv(output_file, index=False)
print(f"💾 Main dataset saved: {output_file}")

# Save a sample for quick analysis
sample_file = r"C:\Users\HP\Downloads\infosys_SpringBoard\weather_data_sample.csv"
sample_size = min(10000, len(df))
df.sample(sample_size).to_csv(sample_file, index=False)
print(f"💾 Sample dataset ({sample_size} rows) saved: {sample_file}")

# Save cleaning report
report_file = r"C:\Users\HP\Downloads\infosys_SpringBoard\cleaning_report.txt"
with open(report_file, 'w') as f:
    f.write("WEATHER DATA CLEANING REPORT\n")
    f.write("=" * 50 + "\n")
    f.write(f"Original dataset: {original_rows:,} rows, {original_cols} columns\n")
    f.write(f"Final dataset: {df.shape[0]:,} rows, {df.shape[1]} columns\n")
    f.write(f"Rows removed: {original_rows - df.shape[0]:,}\n")
    f.write(f"Missing values handled: {original_missing}\n")
    f.write(f"Remaining missing values: {df.isnull().sum().sum()}\n")
    f.write(f"New features created: {df.shape[1] - original_cols}\n")

print(f"📄 Cleaning report saved: {report_file}")

# =============================================================================
# STEP 7: GENERATE BASIC STATISTICS (No Visualization)
# =============================================================================
print(f"\n" + "=" * 70)
print("BASIC STATISTICS SUMMARY")
print("=" * 70)

# Show basic stats for key numerical columns
key_columns = ['temperature_celsius', 'humidity', 'wind_kph', 'pressure_mb']
available_keys = [col for col in key_columns if col in df.columns]

if available_keys:
    print("\n📊 Key Statistics:")
    stats = df[available_keys].describe()
    print(stats.round(2))
else:
    print("Key columns not found in dataset")

# =============================================================================
# FINAL SUCCESS MESSAGE
# =============================================================================
print(f"\n" + "=" * 70)
print("🎉 DATA CLEANING COMPLETED SUCCESSFULLY!")
print("=" * 70)
print(f"📁 Output files created:")
print(f"   • weather_data_cleaned.csv - Full cleaned dataset ({df.shape[0]:,} rows)")
print(f"   • weather_data_sample.csv  - Sample for quick analysis")
print(f"   • cleaning_report.txt      - Detailed cleaning report")
print(f"\n📊 Final Dataset Stats:")
print(f"   • Rows: {df.shape[0]:,}")
print(f"   • Columns: {df.shape[1]}")
print(f"   • Missing Values: {df.isnull().sum().sum()}")
print(f"   • Duplicates: {df.duplicated().sum()}")
print(f"\n🎯 NEXT STEP: Your data is now ready for analysis!")
print("   You can proceed with exploratory data analysis and insights generation.")

# Show first few rows of cleaned data
print(f"\n🔍 First 2 rows of cleaned data:")
print(df.head(2))