# Brand Surge Dashboard - Quick Start Guide

## 🎯 Overview

The Brand Surge Analytics Dashboard is a production-ready Streamlit application that combines CSV and JSON data sources to provide real-time brand sentiment monitoring across multiple brands.

## 📂 Project Structure

```
brandsurge.ai/
├── .streamlit/
│   └── config.toml                    # Dark theme configuration
├── data/
│   ├── csv/                           # CSV data files
│   │   └── your-brand.csv
│   ├── json/                          # JSON data files
│   │   ├── nike_sample.json
│   │   └── adidas_sample.json
│   └── README.md                      # Data directory guide
├── app.py                             # Main dashboard application
├── requirements.txt                   # Python dependencies
├── DASHBOARD_README.md               # Comprehensive documentation
└── QUICK_START.md                    # This file
```

## 🚀 Installation & Running

### Step 1: Install Dependencies

```powershell
pip install streamlit pandas numpy plotly
```

Or use requirements.txt:

```powershell
pip install -r requirements.txt
```

### Step 2: Configure Data Sources

Open `app.py` and locate the `DATA_SOURCES` configuration (around line 85):

```python
CSV_DIR = "data/csv"
JSON_DIR = "data/json"

DATA_SOURCES = [
    # CSV files (place in data/csv/)
    # {
    #     "path": f"{CSV_DIR}/your-brand.csv",
    #     "type": "csv",
    #     "brand": "Your Brand"
    # },
    
    # JSON files (place in data/json/)
    {
        "path": f"{JSON_DIR}/nike_sample.json",
        "type": "json",
        "brand": "Nike"
    },
    {
        "path": f"{JSON_DIR}/adidas_sample.json",
        "type": "json",
        "brand": "Adidas"
    },
]
```

### Step 3: Run the Dashboard

```powershell
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

## 🎨 Dashboard Features

### Left Sidebar
- **Navigation**: Static menu items (Dashboard, Campaigns, Metrics, etc.)
- **Brand Selector**: Switch between loaded brands dynamically
- **Date Range Filter**: Filter data by date range
- **Metric Selector**: Choose metric for channel performance chart

### Main Dashboard Area

#### Top Row - KPI Cards
1. **Sentiment Index** (0-100): Overall sentiment health
2. **Trend Velocity** (%): 14-day engagement trend
3. **Share of Voice** (%): Brand mentions vs all brands
4. **Run Analytics** button: Refresh dashboard

#### Middle Section - Charts
- **Channel Performance**: Bar chart showing metrics by source (Twitter, News, etc.)
- **Geo Sentiment Heatmap**: Sentiment scores by country
- **Live Metrics Panel** (right side):
  - Marketing Health Score gauge
  - 7-day engagement trendline
  - Key statistics

#### Bottom Section - Recommendations
- AI-powered insights summary
- Action buttons:
  - Generate Variant
  - Launch Social Agents
  - Simulate ROI
  - Add to Campaign

## 📊 Adding Your Own Data

### Option 1: Add CSV File

1. Place your CSV file in the `data/csv/` directory
2. Ensure it has these columns (at minimum):
   - `Date`, `Sentiment`, `Source`, `Engagement`, `Views`, `Reach`
3. Add to `DATA_SOURCES`:

```python
{
    "path": f"{CSV_DIR}/your-brand.csv",
    "type": "csv",
    "brand": "Your Brand Name"
}
```

### Option 2: Add JSON File

1. Create a JSON file in `data/json/` directory with an array of objects:

```json
[
  {
    "Date": "2025-11-15",
    "Headline": "Product Launch",
    "Source": "Twitter",
    "Sentiment": "positive",
    "Engagement": 1500,
    "Views": 5000,
    "Reach": 10000,
    "Country": "USA",
    "brand": "My Brand"
  }
]
```

2. Add to `DATA_SOURCES`:

```python
{
    "path": f"{JSON_DIR}/mybrand.json",
    "type": "json",
    "brand": "My Brand"
}
```

### Option 3: Multi-Brand JSON

Create one JSON file in `data/json/` with multiple brands:

```json
[
  {"brand": "Nike", "Date": "2025-11-15", "Sentiment": "positive", ...},
  {"brand": "Adidas", "Date": "2025-11-14", "Sentiment": "neutral", ...}
]
```

Add to config with `"brand": None` to use the brand field from data:

```python
{
    "path": f"{JSON_DIR}/multi-brands.json",
    "type": "json",
    "brand": None
}
```

## 🔧 Customization Tips

### Change Theme Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#8b5cf6"      # Change accent color
backgroundColor = "#0f172a"    # Change main background
```

### Modify Metrics Calculation

All metric formulas are in the `compute_metrics()` function in `app.py` (around line 250).

Example - Change Sentiment Index formula:

```python
# Current: ((avg_sentiment + 1) / 2) * 100
# Custom: Scale differently
metrics['sentiment_index'] = (avg_sentiment * 50) + 50
```

### Add New Chart

In the `render_main_charts()` function (around line 400), add:

```python
with col3:  # Add third column
    st.markdown("### My Custom Chart")
    # Your Plotly/Altair chart here
```

## 🧪 Testing Multi-Brand Support

To test with all sample data:

1. Edit `DATA_SOURCES` in `app.py`:

```python
DATA_SOURCES = [
    {"path": f"{CSV_DIR}/your-brand.csv", "type": "csv", "brand": "Your Brand"},
    {"path": f"{JSON_DIR}/nike_sample.json", "type": "json", "brand": "Nike"},
    {"path": f"{JSON_DIR}/adidas_sample.json", "type": "json", "brand": "Adidas"},
]
```

2. Run the dashboard
3. Use the brand selector in the sidebar to switch between brands
4. Watch metrics update automatically

## ⚡ Performance Tips

- **Cache Duration**: Data is cached for 1 hour by default
- **Date Filtering**: Use smaller date ranges for faster rendering
- **Large Datasets**: Consider loading data from a database instead of files

## 🐛 Common Issues

### Issue: "No data loaded"
**Solution**: Check file paths in `DATA_SOURCES` are correct and files exist

### Issue: Charts not showing
**Solution**: Ensure required columns exist: `Date`, `Source`, `Sentiment`, `Country`

### Issue: Brand not appearing in selector
**Solution**: Verify the `brand` column exists in your data or is specified in config

## 📞 Next Steps

1. **Read full documentation**: See `DASHBOARD_README.md` for detailed API integration guide
2. **Customize metrics**: Modify formulas in `compute_metrics()`
3. **Add more visualizations**: Extend `render_main_charts()`
4. **Connect to live data**: Implement API loader function

## 🎓 Key Code Locations

| Feature | Function | Line (approx) |
|---------|----------|---------------|
| Data loading | `load_data()` | 140 |
| Metric calculations | `compute_metrics()` | 250 |
| KPI cards | `render_kpis()` | 350 |
| Charts | `render_main_charts()` | 400 |
| Recommendations | `render_recommendations()` | 550 |

---

**Ready to analyze your brand data! 🚀**
