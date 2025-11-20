# ClimateScope: Visualizing Global Weather Trends

## Overview
Analysis of global weather patterns using the Global Weather Repository dataset from Kaggle. This project aims to uncover seasonal trends, regional variations, and extreme weather events through data analysis and visualization.

## Dataset
- **Source**: [Global Weather Repository - Kaggle](https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository)
- **Records**: 107,573 observations
- **Coverage**: 211 countries, 254 locations
- **Time Period**: 18 months (May 2024 - Nov 2025)
- **Variables**: Temperature, humidity, precipitation, wind speed, air quality metrics

## Project Structure
```
climatescope-project/
├── data/
│   ├── processed/         # Cleaned datasets
│   └── outputs/           # Analysis reports
├── scripts/
│   ├── data_cleaning.py   # Data preprocessing pipeline
│   └── data_analysis.py   # Exploratory analysis
└── docs/
    └── milestone1_summary.md  # Detailed findings
```

## Setup

### Installation
```bash
# Clone repository
git clone https://github.com/namannnt/-climatescope-project.git
cd climatescope-project

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Scripts
```bash
# Data cleaning
python scripts/data_cleaning.py

# Data analysis
python scripts/data_analysis.py
```

## Milestones

### ✅ Milestone 1: Data Preparation & Analysis (Complete)
- Data cleaning and preprocessing
- Quality assessment (100% completeness, 0 duplicates)
- Statistical analysis and reporting
- Geographic and temporal coverage analysis

### 🔄 Milestone 2: Visualization (In Progress)
- Interactive charts with Plotly
- Geographic heat maps
- Dashboard development with Streamlit

## Key Findings
- **Temperature**: Global average 22.54°C (range: -24.9°C to 49.2°C)
- **Air Quality**: 52.2% locations have "Good" rating
- **Coverage**: 211 countries analyzed across 18 months
- **Data Quality**: Zero missing values, zero duplicates

## Technologies
- Python 3.x
- Pandas, NumPy
- Plotly, Streamlit (upcoming)
- Folium (upcoming)
