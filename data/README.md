# Data Directory

This directory contains all data sources for the Brand Surge Analytics Dashboard.

## 📁 Directory Structure

```
data/
├── csv/          # Place all CSV files here
│   └── your-brand.csv
└── json/         # Place all JSON files here
    ├── nike_sample.json
    └── adidas_sample.json
```

## 📊 Adding New Data

### CSV Files

1. Place your CSV file in the `csv/` directory
2. Update `DATA_SOURCES` in `app.py`:

```python
{
    "path": f"{CSV_DIR}/your-brand.csv",
    "type": "csv",
    "brand": "Your Brand Name"
}
```

### JSON Files

1. Place your JSON file in the `json/` directory
2. Update `DATA_SOURCES` in `app.py`:

```python
{
    "path": f"{JSON_DIR}/your-brand.json",
    "type": "json",
    "brand": "Your Brand Name"  # Or None to use brand from data
}
```

## 📋 Required Data Schema

Your CSV/JSON files should include these columns:

- `Date` - Publication date
- `Sentiment` - positive/neutral/negative/unknown
- `Source` - Channel (Twitter, News, etc.)
- `Engagement` - Engagement count
- `Views` - View count
- `Reach` - Audience reach
- `Country` - Geographic location
- `brand` - Brand name (optional, can be set in config)

## 🔍 Example Data

Check the sample JSON files in `json/` directory for format examples:
- `nike_sample.json` - 5 sample records
- `adidas_sample.json` - 5 sample records

## 🚀 Quick Start

1. Add your CSV files to `csv/`
2. Add your JSON files to `json/`
3. Update `DATA_SOURCES` in `app.py`
4. Run: `streamlit run app.py`

## 📝 Notes

- All file paths in `DATA_SOURCES` use the `CSV_DIR` and `JSON_DIR` constants
- This keeps your data organized and paths easy to manage
- You can have multiple CSV and JSON files for different brands
- The dashboard will combine all sources into one unified view
