# BrandSurge.ai Dashboard - Setup Instructions

## Overview
This Streamlit dashboard provides comprehensive brand sentiment analytics with support for multiple data sources including CSV files and Meltwater API data.

## Prerequisites
- Python 3.11 or higher

## Setup

### 1. Create Virtual Environment
```powershell
py -m venv venv
```

### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install streamlit pandas plotly
```

## Running the Dashboard

### Start the Application
```powershell
.\venv\Scripts\streamlit.exe run app.py
```

Or, if virtual environment is already activated:
```powershell
streamlit run app.py
```

The dashboard will open automatically in your default browser at http://localhost:8501

## Data Sources

The dashboard supports multiple data sources configured in `DATA_SOURCES`:

### Supported Formats

1. **CSV Files** (Place in `data/csv/`)
   - Standard flat CSV with columns matching the 36-field schema
   - Example: `Lockheed Martin - Lockheed Martin.csv`

2. **JSON Files** (Place in `data/json/`)
   - Flat JSON with records matching the 36-field schema
   - Examples: `nike_sample.json`, `adidas_sample.json`

3. **Meltwater API Data** (Place in `data/json/`)
   - Nested Meltwater social listening data
   - Automatically transformed to dashboard schema
   - Examples: `meltwaterdataset1.json`, `meltwaterdataset2.json`

### Current Data Sources

- **Lockheed Martin** (CSV) - 10,598 records
- **Nike** (JSON) - Sample data
- **Adidas** (JSON) - Sample data
- **Coca-Cola Dataset 1** (Meltwater) - Social listening data
- **Coca-Cola Dataset 2** (Meltwater) - Social listening data

## Features

- **Multi-Brand Analytics**: Switch between brands using the sidebar selector
- **Dark Theme**: Modern dark UI with rounded cards and gradient backgrounds
- **KPI Metrics**:
  - Sentiment Index (0-100 scale)
  - Trend Velocity (% change)
  - Share of Voice (brand visibility)
  - Health Score (overall brand health)
- **Visualizations**:
  - Sentiment gauge
  - Top sources bar chart
  - Sentiment trend over time
  - Geographic heatmap
  - Content type distribution
- **AI-Powered Recommendations**: Strategic insights based on data analysis

## Meltwater Data Transformation

The dashboard automatically transforms Meltwater's nested API format into the flat 36-field schema:

- **Date** ← `published_date`
- **Sentiment** ← `enrichments.sentiment`
- **Source** ← `source.name`
- **Engagement** ← `metrics.engagement.total`
- **Reach** ← `source.metrics.reach` or `metrics.estimated_views`
- **Social Echo** ← `metrics.social_echo.{facebook, x, reddit}`
- **Location** ← `location.{country_code, state, city}`
- **Content** ← `content.{title, body, image}`

## Troubleshooting

### Virtual Environment Not Activating
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Streamlit Command Not Found
Always use the full path when running from outside the venv:
```powershell
.\venv\Scripts\streamlit.exe run app.py
```

### Port Already in Use
If port 8501 is occupied:
```powershell
.\venv\Scripts\streamlit.exe run app.py --server.port 8502
```

## Project Structure

```
brandsurge.ai/
├── app.py                      # Main Streamlit application
├── data/
│   ├── csv/                    # CSV data files
│   │   └── Lockheed Martin - Lockheed Martin.csv
│   └── json/                   # JSON data files
│       ├── nike_sample.json
│       ├── adidas_sample.json
│       ├── meltwaterdataset1.json
│       └── meltwaterdataset2.json
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── venv/                       # Virtual environment (created)
└── SETUP_INSTRUCTIONS.md       # This file
```

## Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Server settings
- Browser behavior

## Adding New Data Sources

1. Place your data file in the appropriate directory (`data/csv/` or `data/json/`)
2. Add a new entry to `DATA_SOURCES` in `app.py`:

```python
{
    "path": f"{CSV_DIR}/your-file.csv",  # or JSON_DIR
    "type": "csv",  # or "json" or "meltwater"
    "brand": "Your Brand Name"
}
```

3. Restart the dashboard

## Support

For issues or questions, refer to the dashboard_prd.md for requirements and specifications.
