# Brand Surge Analytics Dashboard

A modern, dark-themed Streamlit dashboard for multi-brand sentiment monitoring and analytics. Supports both CSV and JSON data sources with unified schema normalization.

## 🚀 Features

- **Multi-Brand Support**: Seamlessly switch between multiple brands
- **Unified Data Loading**: Handles both CSV and JSON data formats
- **Dark Modern UI**: Navy/charcoal theme with bright accent colors
- **Interactive Analytics**: 
  - Sentiment Index (0-100 scale)
  - Trend Velocity (% change)
  - Share of Voice across brands
  - Marketing Health Score
- **Rich Visualizations**:
  - Channel Performance charts
  - Geographic Sentiment heatmaps
  - 7-day engagement trends
  - Real-time gauges
- **Agentic Recommendations**: AI-powered insights and action buttons

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies

```powershell
pip install streamlit pandas numpy plotly
```

Or use the requirements file:

```powershell
pip install -r requirements.txt
```

## 🎯 Quick Start

1. **Place your data files** in the organized data directories:
   - CSV files → `data/csv/` directory
   - JSON files → `data/json/` directory

2. **Configure data sources** in `app.py`:
   ```python
   DATA_SOURCES = [
       {"path": f"{CSV_DIR}/your-brand.csv", "type": "csv", "brand": "Your Brand"},
       {"path": f"{JSON_DIR}/your-brand.json", "type": "json", "brand": "Your Brand"},
   ]
   ```

3. **Run the dashboard**:
   ```powershell
   streamlit run app.py
   ```

4. **Open your browser** at `http://localhost:8501`

## 📊 Data Format

### Expected Schema

Both CSV and JSON sources should contain these columns:

| Column | Type | Description |
|--------|------|-------------|
| Date | datetime | Publication date |
| Headline | string | Article/post title |
| Source | string | Channel (Twitter, news, etc.) |
| Sentiment | string | positive/neutral/negative/unknown |
| Country | string | Geographic location |
| Engagement | numeric | Engagement metrics |
| Views | numeric | View count |
| Reach | numeric | Audience size |
| brand | string | Brand name (auto-added if missing) |

### CSV Example
```csv
Date,Headline,Source,Sentiment,Country,Engagement,Views,Reach
2025-01-15,Product Launch,Twitter,positive,USA,1250,5000,10000
```

### JSON Example
```json
[
  {
    "Date": "2025-01-15",
    "Headline": "Product Launch",
    "Source": "Twitter",
    "Sentiment": "positive",
    "Country": "USA",
    "Engagement": 1250,
    "Views": 5000,
    "Reach": 10000,
    "brand": "Nike"
  }
]
```

## 🔧 Configuration

### Adding New Data Sources

1. **Place files in organized directories**:
   - CSV files → `data/csv/`
   - JSON files → `data/json/`

2. **Edit the `DATA_SOURCES` list in `app.py`**:

```python
DATA_SOURCES = [
    # CSV source
    {
        "path": f"{CSV_DIR}/your-brand.csv",
        "type": "csv",
        "brand": "Your Brand Name"
    },
    
    # JSON source with brand in data
    {
        "path": f"{JSON_DIR}/multi-brand.json",
        "type": "json",
        "brand": None  # Will use 'brand' field from JSON
    },
    
    # JSON source with brand override
    {
        "path": f"{JSON_DIR}/data.json",
        "type": "json",
        "brand": "Override Brand"  # Overrides JSON 'brand' field
    },
]
```

### Brand Name Resolution

The dashboard determines brand names in this order:
1. `brand` field in the data (CSV/JSON)
2. `brand` parameter in DATA_SOURCES config
3. Filename (e.g., "Nike.json" → "Nike")

### Customizing the Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#8b5cf6"      # Purple accent
backgroundColor = "#0f172a"    # Dark navy background
secondaryBackgroundColor = "#1e293b"  # Card background
textColor = "#f1f5f9"         # Light text
```

## 📈 Metrics Explained

### Sentiment Index (0-100)
- Converts sentiment to numeric: positive=+1, neutral=0, negative=-1
- Averages across all records
- Scales to 0-100: `((avg + 1) / 2) * 100`

### Trend Velocity (%)
- Compares last 14 days vs previous 14 days
- Metric: sum of Engagement (or mention count)
- Formula: `((Recent - Previous) / Previous) * 100`

### Share of Voice (%)
- Brand mentions vs total mentions across all brands
- Formula: `(Brand mentions / Total mentions) * 100`

### Marketing Health Score (0-100)
Composite score combining:
- 40% Sentiment Index
- 30% Normalized Engagement
- 30% Normalized Reach

## 🔄 Future API Integration

To adapt for API data sources:

1. **Create API loader function**:
```python
@st.cache_data(ttl=300)
def load_from_api(endpoint: str, brand: str) -> pd.DataFrame:
    response = requests.get(endpoint)
    data = response.json()
    df = pd.json_normalize(data)
    df['brand'] = brand
    return df
```

2. **Add API source type**:
```python
DATA_SOURCES = [
    {
        "type": "api",
        "endpoint": "https://api.example.com/brand-data",
        "brand": "Nike"
    }
]
```

3. **Update load_data() function**:
```python
if source_type == 'api':
    df = load_from_api(source['endpoint'], source['brand'])
```

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Sidebar              │ Main Dashboard                       │
│ ─────────           │ ─────────────                        │
│ • Dashboard          │ [Sentiment] [Trend] [Share] [Run]    │
│ • Campaigns          │                                      │
│ • Metrics            │ ┌──────────┐ ┌──────────┐ ┌────┐   │
│                      │ │ Channel  │ │ Geo Heat │ │Live│   │
│ [Brand Selector]     │ │Performance│ │   Map    │ │Metr│   │
│ [Date Range]         │ └──────────┘ └──────────┘ └────┘   │
│ [Metric Selector]    │                                      │
│                      │ [Agentic Recommendations Panel]      │
└─────────────────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### "No data loaded" error
- Check that CSV/JSON files exist at specified paths
- Verify file paths are correct in `DATA_SOURCES`
- Ensure files have proper permissions

### Missing columns warning
- Verify your data has required columns (Date, Sentiment, Source)
- Check column name spelling (case-sensitive)
- Review schema in file header comments

### Slow performance
- Reduce date range filter
- Use `@st.cache_data` for heavy computations
- Limit number of data sources loaded simultaneously

## 📝 License

MIT License - feel free to use and modify for your projects.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

**Built with Streamlit 🎈 | Powered by Brand Surge AI**
