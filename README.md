# Climatescope Project

## About
This project analyzes weather data from around the world using the Global Weather Repository dataset from Kaggle.

## Project Structure
```
climatescope-project/
├── data/
│   ├── raw/          # Original dataset (not tracked in git)
│   ├── processed/    # Cleaned data
│   └── outputs/      # Analysis results
├── notebooks/        # Jupyter notebooks for exploration
├── scripts/          # Python scripts
│   ├── data_cleaning.py
│   ├── data_analysis.py
│   └── visualizations.py
├── docs/             # Documentation
└── app/              # Streamlit app (future)
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/climatescope-project.git
cd climatescope-project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Download Dataset
- Download the Global Weather Repository dataset from Kaggle
- Place the dataset in `data/raw/` folder

## Workflow

### Working on a New Feature
```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Make your changes, then commit
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature/your-feature-name
```

### After PR is Merged
```bash
# Switch back to main and update
git checkout main
git pull origin main
```

## Progress

### Milestone 1: Data Preparation & Initial Analysis (Completed)
- [x] Environment setup and dependency installation
- [x] Dataset acquisition from Kaggle (107,573 records)
- [x] Comprehensive data quality assessment
- [x] Data cleaning and preprocessing pipeline
- [x] Temporal feature engineering
- [x] Statistical analysis and reporting
- [x] Data aggregation (daily country-level metrics)
- [x] Documentation and code organization

### Milestone 2: Data Visualization (In Progress)
- [ ] Temperature trend visualizations
- [ ] Geographic heat maps
- [ ] Air quality distribution charts
- [ ] Interactive Plotly dashboards
- [ ] Correlation analysis

## Project Overview

This project is part of an internship focused on climate data analysis. The dataset contains comprehensive weather and air quality information from 211 countries and 254 unique locations worldwide, spanning 18 months of observations.

### Key Features
- **Data Cleaning Pipeline**: Automated preprocessing and validation
- **Exploratory Analysis**: Comprehensive statistical analysis of weather patterns
- **Air Quality Assessment**: PM2.5, PM10, and EPA index analysis
- **Geographic Coverage**: Global dataset with 107,573+ observations

### Technologies Used
- **Python 3.x**: Core programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations (upcoming)
- **Streamlit**: Dashboard development (upcoming)
- **Folium**: Geographic visualizations (upcoming)
