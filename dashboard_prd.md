# Brand Surge – Dynamic Sentiment Dashboard Framework

This document describes the full framework and structure for a **Streamlit-based brand sentiment dashboard** that uses **both CSV and JSON data sources**. It is meant as an architectural reference for building the app with an LLM (e.g., Claude Sonnet) and for future manual development.

The dashboard should mimic a modern “brand analytics” UI:

- Dark theme (navy/charcoal background, bright accents).
- Left navigation sidebar.
- KPI strip across the top.
- Central charts (Channel Performance, Geo Sentiment).
- Right column of “Live Metrics”.
- Bottom “Agentic Recommendations” panel with CTA buttons.

The coding prompt you use for Claude should follow this framework closely.


---

## 1. Tech Stack

**Language & runtime**

- Python 3.10+ (or current stable on your machine)

**Core libraries**

- `streamlit` – web app framework
- `pandas` – data wrangling
- `numpy` – numeric helpers
- `plotly` *or* `altair` – charts (heatmap, line, bar, gauge)
- `python-dateutil` (optional) – date parsing utilities

**Optional**

- `pyyaml` – if you eventually move data source config into a YAML file instead of a Python list


### 1.1 Suggested `requirements.txt`

```text
streamlit
pandas
numpy
plotly
python-dateutil
altair
(You can adjust this to your preferred charting library or pin versions later.)

2. Project Structure
Recommended minimal structure for the repo:

text
Copy code
.
├─ app.py                        # Main Streamlit app
├─ requirements.txt
├─ data/
│  ├─ Lockheed Martin - Lockheed Martin.csv
│  ├─ nike.json                  # example JSON brand file
│  ├─ adidas.json                # example JSON brand file
│  └─ ...
├─ .streamlit/
│  └─ config.toml                # Dark theme configuration
└─ docs/
   └─ BRAND_SURGE_DASHBOARD_FRAMEWORK.md   # This document
Note: In the Claude prompt we refer to "Lockheed Martin - Lockheed Martin.csv"
and also show /mnt/data/... as an example path. In your actual repo, paths
should match the structure above (data/ folder). Update the prompt’s paths
if needed so everything is consistent.

3. Data Model
The dashboard consumes multiple data sources (CSV and JSON) and merges them into a single unified DataFrame.

3.1 Source files
CSV
Example: data/Lockheed Martin - Lockheed Martin.csv
This is your Meltwater-style export and defines the canonical schema.

JSON

May contain one brand or many brands.

May be one file per brand (e.g., nike.json, adidas.json).

JSON structure is “normalized”: an array of objects, each object mapping directly to the CSV fields.

3.2 Core schema (canonical columns)
From the CSV, the core columns you care about include (names may vary slightly but the idea is):

Date

Headline

URL

Opening Text

Hit Sentence

Source (social platform / publisher)

Influencer

Country

Subregion

State

City

Language

Reach

Desktop Reach

Mobile Reach

Twitter Social Echo

Facebook Social Echo

Reddit Social Echo

Earned Traffic

National Viewership

AVE

Sentiment (categorical: positive, neutral, negative, unknown)

Key Phrases

Input Name

Keywords

Document Tags

Engagement

Hashtags

Views

Estimated Views

Custom Categories

Plus a derived brand column (see below).

3.3 Unified DataFrame schema
After loading from CSV and JSON, your unified DataFrame should have at least:

brand – string identifier ("Lockheed Martin", "Nike", etc.)

date – parsed datetime (from Date)

source – channel/platform (normalized from Source)

country, state, subregion, city – geographic attributes

sentiment_raw – original string (positive / neutral / negative / unknown)

sentiment_score – numeric sentiment mapping

reach, desktop_reach, mobile_reach

views, estimated_views

engagement

twitter_social_echo, facebook_social_echo, reddit_social_echo

ave, earned_traffic, national_viewership

optional text columns (headline, opening_text, etc.) for recommendations

This keeps numeric metrics and key text available for charts and summary text.

4. Configuration – Data Sources
At the top of app.py, define the data sources in a simple list of dicts:

python
Copy code
DATA_SOURCES = [
    {
        "path": "data/Lockheed Martin - Lockheed Martin.csv",
        "type": "csv",
        "brand": "Lockheed Martin",
    },
    {
        "path": "data/nike.json",
        "type": "json",
        "brand": "Nike",          # fallback brand if field not present in JSON
    },
    {
        "path": "data/adidas.json",
        "type": "json",
        "brand": "Adidas",
    },
    # Add more sources here...
]
The Claude prompt you use should tell the model to:

Implement a load_data(sources: list) -> pd.DataFrame function.

Use this config to load CSV and JSON.

Ensure a brand column is present in the final DataFrame.

Normalize column names so CSV and JSON align with the schema in Section 3.

5. Application Flow
High-level flow for app.py:

Configuration & imports

Import libraries, set DATA_SOURCES.

Call st.set_page_config(layout="wide", page_title="Brand Analytics Dashboard").

Data loading & preparation

df_raw = load_data(DATA_SOURCES)

df = prepare_data(df_raw)

Parse dates.

Normalize column names (snake_case).

Map sentiment categories → numeric scores.

Drop or handle missing values.

Brand list & user selections

brands = get_brand_list(df)

Sidebar selectbox for brand.

Sidebar / main filters:

Date range (slider or date picker).

Metric selector for Channel Performance.

Filtering

df_brand = filter_by_brand_and_date(df, selected_brand, date_range)

Compute brand-specific metrics and aggregates.

Metrics computation

metrics = compute_metrics(df_brand, df_all=df)

Sentiment Index

Trend Velocity

Share of Voice

Marketing Health Score

Supporting KPIs (total mentions, reach, etc.)

Rendering

render_sidebar(...)

render_kpis(metrics)

render_main_charts(df_brand, metric_choice)

render_right_panel(df_brand, metrics)

render_recommendations(df_brand, metrics)

Interactivity

Run Analytics button triggers recomputation / toasts.

Filters automatically recompute KPIs and charts (Streamlit does this on interaction).

6. Functions and Responsibilities
The Claude prompt should instruct the model to implement (or similar):

6.1 Data layer
python
Copy code
def load_data(sources: list[dict]) -> pd.DataFrame:
    """
    Load and combine multiple CSV/JSON data sources into a single DataFrame.

    - Reads each 'path' in sources.
    - Uses 'type' ('csv' or 'json') to choose reader.
    - Ensures a 'brand' column:
        - Uses a 'brand' field from the data if present, otherwise
          uses the 'brand' value in the source dict.
    - Normalizes key column names to a canonical schema.
    - Concatenates all records and returns a unified DataFrame.
    """
    ...


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and enrich the unified DataFrame.

    - Parse 'Date' column to datetime -> 'date'.
    - Normalize column names (lowercase, underscores).
    - Create 'sentiment_raw' (original) and 'sentiment_score' (numeric):
        positive -> 1, neutral/unknown -> 0, negative -> -1 (for example).
    - Add any derived fields needed for metrics (e.g., 'mentions' = 1 per row).
    """
    ...
6.2 Filtering and brand handling
python
Copy code
def get_brand_list(df: pd.DataFrame) -> list[str]:
    """Return sorted unique brand names from df['brand']."""
    ...


def filter_by_brand_and_date(
    df: pd.DataFrame,
    brand: str,
    date_range: tuple[pd.Timestamp, pd.Timestamp] | None
) -> pd.DataFrame:
    """
    Filter the DataFrame for the_SELECTED brand and optional date range.
    """
    ...
6.3 Metric computation
python
Copy code
def compute_metrics(
    df_brand: pd.DataFrame,
    df_all: pd.DataFrame
) -> dict:
    """
    Compute all high-level metrics for the selected brand.

    Should return a dict such as:
    {
        "sentiment_index": float,
        "trend_velocity_pct": float,
        "share_of_voice_pct": float,
        "marketing_health_score": float,
        "total_mentions": int,
        "total_reach": float,
        "avg_engagement": float,
        "recent_trend_series": pd.Series or pd.DataFrame,
        ...
    }

    Notes:
    - Sentiment index: e.g., map scores -1..1 -> 0..100:
        index = (sentiment_score_mean + 1) / 2 * 100
    - Trend velocity: percent change of a key metric (mentions, views, engagement)
      between the most recent N days and the previous N days.
    - Share of voice: brand_mentions / total_mentions_across_brands * 100.
    - Marketing health score: weighted combination of normalized sentiment,
      engagement, and reach (document weighting in comments).
    """
    ...
6.4 Layout & rendering
python
Copy code
def render_sidebar(df: pd.DataFrame) -> tuple[str, tuple, str]:
    """
    Render the left sidebar:
    - Title ('Brand Surge')
    - Navigation labels (Dashboard, Uplifted Feeds, etc.)
    - Brand selector (returns selected brand)
    - Date range filter (returns start/end)
    - Metric selector for Channel Performance

    Returns:
        selected_brand, date_range, metric_choice
    """
    ...


def render_kpis(metrics: dict) -> None:
    """
    Render the top KPI row using st.columns and st.metric:
    - Sentiment Index
    - Trend Velocity
    - Share of Voice
    - Possibly one more metric (e.g., Total Mentions)
    Includes a 'Run Analytics' button on the right side.
    """
    ...
python
Copy code
def render_main_charts(df_brand: pd.DataFrame, metric_choice: str) -> None:
    """
    Render the central charts:

    1) Channel Performance:
       - x-axis: Source or Date
       - y-axis: selected metric (mentions, views, engagement, etc.)
       - Implemented as bar or line chart.

    2) Geo Sentiment Heat Map:
       - x-axis: Country
       - y-axis: optional dimension (e.g., Subregion)
       - Color: aggregated sentiment score or mention volume.
       - Use Plotly or Altair for a heatmap-like visualization.
    """
    ...


def render_right_panel(df_brand: pd.DataFrame, metrics: dict) -> None:
    """
    Render the right-hand 'Live Metrics' column:

    - Marketing Health Score (gauge or stylized bar).
    - 7-Day Trendline mini chart (recent_trend_series).
    - KPIs in small cards:
        - Total mentions
        - Total reach
        - Average engagement
        - Possibly API usage / agents metrics (placeholder).
    """
    ...


def render_recommendations(df_brand: pd.DataFrame, metrics: dict) -> None:
    """
    Render the bottom 'Agentic Recommendations' panel:

    - A summary sentence/paragraph describing:
        - Dominant sentiment
        - Top channel by engagement
        - Any notable upward/downward trend.
    - Buttons:
        - 'Generate Variant'
        - 'Launch Social Agents'
        - 'Simulate ROI'
        - 'Add to Campaign'
      Each button may display st.toast or st.info for now.
    """
    ...
6.5 Main entrypoint
Skeleton of app.py:

python
Copy code
import streamlit as st
import pandas as pd
from typing import Tuple

# --- config & constants ------------------------------------------------------

DATA_SOURCES = [
    {"path": "data/Lockheed Martin - Lockheed Martin.csv", "type": "csv", "brand": "Lockheed Martin"},
    # {"path": "data/nike.json", "type": "json", "brand": "Nike"},
    # {"path": "data/adidas.json", "type": "json", "brand": "Adidas"},
]

# --- Streamlit page config ---------------------------------------------------

st.set_page_config(
    page_title="Brand Analytics Dashboard",
    layout="wide",
)

# --- main logic --------------------------------------------------------------

def main() -> None:
    df_raw = load_data(DATA_SOURCES)
    df = prepare_data(df_raw)

    selected_brand, date_range, metric_choice = render_sidebar(df)

    df_brand = filter_by_brand_and_date(df, selected_brand, date_range)

    metrics = compute_metrics(df_brand, df_all=df)

    render_kpis(metrics)
    render_main_charts(df_brand, metric_choice)
    render_right_panel(df_brand, metrics)
    render_recommendations(df_brand, metrics)


if __name__ == "__main__":
    main()
This structure is exactly what the prompt should nudge Claude to generate.

7. UI Layout Details
The Claude prompt already describes the layout, but here is the condensed blueprint to keep in sync:

7.1 Sidebar
Title: Brand Surge

Navigation (static text):

Dashboard

Uplifted Feeds

Campaigns

Orchestration

Metrics & Attribution

Social Agents

Integrations

Security

Brand selector: st.selectbox("Brand", brands)

Date range selector: st.date_input or similar

Metric selector for Channel Performance

7.2 Top KPI row (main area)
3–4 st.metric tiles:

Sentiment Index (0–100)

Trend Velocity (%)

Share of Voice (%)

Optional: Total Mentions / Reach

“Run Analytics” button to the far right.

7.3 Middle center: charts
Channel Performance chart

Based on Source or Date.

Metric from the metric selector.

Geo Sentiment Heat Map

Aggregated by Country (and optionally Subregion).

Uses sentiment_score and/or mentions.

7.4 Right column: Live Metrics
Marketing Health Score card with gauge / bar.

7-day trend mini-line chart:

Most recent N days of a key metric.

Additional cards for:

Total mentions

Total reach

Average engagement

Any placeholder metrics for “API Usage”, “Active Agents”, etc.

7.5 Bottom: Recommendations panel
Full-width container with dark card background.

Summary paragraph based on metrics and df_brand.

Bright CTA buttons:

Generate Variant

Launch Social Agents

Simulate ROI

Add to Campaign

8. Theming and Styling
Use Streamlit’s theme system plus minimal CSS to approximate the mockup.

8.1 .streamlit/config.toml example
toml
Copy code
[theme]
base = "dark"
primaryColor = "#7B5CFF"          # Accent purple
backgroundColor = "#050816"      # Deep navy / charcoal
secondaryBackgroundColor = "#111827"
textColor = "#E5E7EB"
font = "sans serif"
You can add a small CSS block in app.py (via st.markdown(..., unsafe_allow_html=True)) to:

Round card corners.

Add subtle shadows.

Space elements more like a product UI.

9. Extensibility
9.1 Adding a new brand
Drop a new CSV or JSON into data/.

Add an entry to DATA_SOURCES:

python
Copy code
DATA_SOURCES.append({
    "path": "data/new_brand.json",
    "type": "json",
    "brand": "New Brand Name",
})
On reload, the new brand appears in the sidebar selectbox and is included in aggregate metrics (e.g., share of voice).

9.2 Moving config to JSON/YAML (optional later)
Instead of editing Python, you could move DATA_SOURCES to a small config file (e.g., config/data_sources.yaml). The loading function would parse YAML and produce the same list of dicts.

9.3 API integration (future)
Once the dashboard is stable:

Replace load_data’s file-reading logic with an API client that:

Calls Meltwater or your backend.

Returns the same unified schema (DataFrame with brand, date, etc.).

Keep the rest of the app unchanged, as all logic depends only on the unified DataFrame, not on the underlying source.

10. Alignment With the Claude Prompt
The development prompt you feed to Claude Sonnet 4.5 should:

Explicitly mention:

STREAMLIT + PANDAS.

CSV + JSON integration via DATA_SOURCES.

The unified loader (load_data) and prepare_data.

The layout sections (sidebar, KPI row, charts, right panel, recommendations).

Metrics and formulas (sentiment index, trend velocity, share of voice, marketing health).

Required helper functions and their responsibilities (as outlined in Section 6).

Request:

A complete app.py.

A config.toml snippet.

A short explanation of the design and how CSV + JSON are used.

The long prompt you already have matches this framework; if you edit the paths or names, keep them synced with:

DATA_SOURCES structure

Function names and responsibilities

The visual sections described above

With this framework in place, you can:

Drop this document into the repo for reference.

Paste the prepared prompt into VS Code’s Claude integration.

Use the generated app.py as a first iteration, then refine visuals and metrics.