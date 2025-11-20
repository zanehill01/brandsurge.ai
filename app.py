"""
Brand Analytics Dashboard - Streamlit Application
==================================================

A modern, dark-themed analytics dashboard for multi-brand sentiment monitoring.
Supports both CSV and JSON data sources with unified schema normalization.

EXPECTED SCHEMA (CSV & JSON):
-----------------------------
Core columns expected in both CSV and JSON sources:
- Date (str/datetime): Publication date
- Headline (str): Article/post title
- URL (str): Source URL
- Opening Text (str): Content preview
- Hit Sentence (str): Matched sentence
- Source (str): Channel (e.g., Twitter, news, blogs)
- Influencer (str): Author/influencer name
- Country, Subregion, State, City (str): Geographic data
- Language (str): Content language
- Reach, Desktop Reach, Mobile Reach (numeric): Audience size
- Twitter Social Echo, Facebook Social Echo, Reddit Social Echo (numeric): Social metrics
- Earned Traffic, National Viewership (numeric): Traffic metrics
- AVE (numeric): Advertising Value Equivalency
- Sentiment (str): positive / neutral / negative / unknown
- Key Phrases (str): Important phrases
- Input Name, Keywords, Document Tags (str): Metadata
- Engagement, Views, Estimated Views (numeric): Engagement metrics
- Hashtags (str): Social hashtags
- Custom Categories (str): Custom tags
- brand (str): Brand name (added if missing)

SENTIMENT INDEX CALCULATION:
----------------------------
Numeric sentiment score per record:
- positive = +1
- neutral = 0
- negative = -1
- unknown/other = 0

Sentiment Index (0-100 scale):
- Compute average sentiment score across records
- Transform: ((avg_score + 1) / 2) * 100
- This maps [-1, 1] → [0, 100]

SHARE OF VOICE CALCULATION:
---------------------------
Per brand: (Brand mentions / Total mentions across all brands) * 100

TREND VELOCITY CALCULATION:
---------------------------
Uses last 14 days vs previous 14 days:
- Metric: sum of Engagement (or Views/Mentions)
- % change = ((Recent - Previous) / Previous) * 100 if Previous > 0 else 0

HOW TO ADD/REMOVE DATA SOURCES:
-------------------------------
Edit the DATA_SOURCES list below:
- For CSV: {"path": "yourfile.csv", "type": "csv", "brand": "BrandName"}
- For JSON: {"path": "yourfile.json", "type": "json", "brand": "BrandName"}
- JSON can have:
  1. A "brand" field per record (use "brand": None in config)
  2. Multiple brands in one file (inferred from data)
  3. Single-brand file (specify "brand": "BrandName")
- Brand name fallback: config → filename → "Unknown"

FUTURE API INTEGRATION:
-----------------------
To adapt for API data:
1. Create load_from_api() function that returns pd.DataFrame
2. Add {"type": "api", "endpoint": "url", "brand": "X"} to DATA_SOURCES
3. Modify load_data() to handle "api" type
4. Normalize API response to match expected schema
5. Cache with @st.cache_data for performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from pathlib import Path

# ============================================================================
# CONFIGURATION - EDIT THIS SECTION TO ADD/REMOVE DATA SOURCES
# ============================================================================

# Directory paths for organized data storage
CSV_DIR = "data/csv"
JSON_DIR = "data/json"

DATA_SOURCES = [
    # CSV files (place all CSV files in data/csv/)
    {
        "path": f"{CSV_DIR}/Lockheed Martin - Lockheed Martin.csv",
        "type": "csv",
        "brand": "Lockheed Martin"
    },
    
    # JSON files (place all JSON files in data/json/)
    {
        "path": f"{JSON_DIR}/nike_sample.json",
        "type": "json",
        "brand": "Nike"  # Use None if brand is in JSON data
    },
    {
        "path": f"{JSON_DIR}/adidas_sample.json",
        "type": "json",
        "brand": "Adidas"
    },
    
    # Meltwater API data (nested structure - will be transformed)
    {
        "path": f"{JSON_DIR}/meltwaterdataset1.json",
        "type": "meltwater",
        "brand": "Coca-Cola"
    },
    {
        "path": f"{JSON_DIR}/meltwaterdataset2.json",
        "type": "meltwater",
        "brand": "Coca-Cola"
    },
]

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    layout="wide",
    page_title="brandsurge.ai",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - DARK THEME WITH ROUNDED CARDS
# ============================================================================

st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0f172a;
    }
    
    /* Adjust main content */
    .main .block-container {
        max-width: 100%;
    }
    
    /* Card styling */
    .card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
        margin: 10px 0;
    }
    
    /* KPI cards with accent colors */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border-left: 4px solid;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-green { border-left-color: #10b981; }
    .kpi-purple { border-left-color: #8b5cf6; }
    .kpi-blue { border-left-color: #3b82f6; }
    .kpi-orange { border-left-color: #f59e0b; }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Recommendation panel */
    .recommendation-panel {
        background: linear-gradient(135deg, #312e81 0%, #1e293b 100%);
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #4c1d95;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
    }
    
    /* Chart containers */
    .chart-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
    }
    
    /* Navigation items */
    .nav-item {
        color: #94a3b8;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background: #334155;
        color: #f1f5f9;
    }
    
    .nav-item.active {
        background: #8b5cf6;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING & PREPARATION FUNCTIONS
# ============================================================================

def transform_meltwater_data(meltwater_records: List[Dict]) -> pd.DataFrame:
    """
    Transform Meltwater API format to flat 36-field schema.
    
    Meltwater structure has nested fields like:
    - author: {name, handle, external_id, profile_url}
    - content: {title, body, byline, image, links, hashtags, mentions}
    - enrichments: {sentiment, language_code, named_entities, keyphrases}
    - metrics: {engagement{total, likes, shares...}, social_echo{facebook, x, reddit}, estimated_views}
    - location: {city, state, country_code, geo{latitude, longitude}}
    - matched: {keywords, inputs[{name, id, type}]}
    - source: {name, type, url}
    
    Maps to 36-field schema used by dashboard.
    """
    transformed_rows = []
    
    for record in meltwater_records:
        try:
            # Extract nested fields safely
            content = record.get('content', {}) or {}
            enrichments = record.get('enrichments', {}) or {}
            metrics = record.get('metrics', {}) or {}
            engagement = metrics.get('engagement', {}) or {}
            social_echo = metrics.get('social_echo', {}) or {}
            location_data = record.get('location', {}) or {}
            source = record.get('source', {}) or {}
            matched = record.get('matched', {}) or {}
            author = record.get('author', {}) or {}
            
            # Build flat row matching 36 fields
            row = {
                # Core fields
                'Date': record.get('published_date', ''),
                'Sentiment': enrichments.get('sentiment', 'neutral'),
                'Source': source.get('name', ''),
                'Engagement': engagement.get('total', 0) or 0,
                'Reach': source.get('metrics', {}).get('reach', 0) or metrics.get('estimated_views', 0) or 0,
                'Views': metrics.get('views', 0) or 0,
                'Estimated Views': metrics.get('estimated_views', 0) or 0,
                'AVE': source.get('metrics', {}).get('ave', 0) or 0,
                
                # Social Echo fields
                'Twitter Social Echo': social_echo.get('x', 0) or 0,
                'Facebook Social Echo': social_echo.get('facebook', 0) or 0,
                'Reddit Social Echo': social_echo.get('reddit', 0) or 0,
                'Total Social Echo': social_echo.get('total', 0) or 0,
                
                # Geographic fields
                'Country': location_data.get('country_code', '').upper() if location_data.get('country_code') else '',
                'State': location_data.get('state', ''),
                'City': location_data.get('city', ''),
                
                # Content fields
                'Title': content.get('title', '') or content.get('opening_text', '') or '',
                'URL': record.get('url', ''),
                'Keywords': ', '.join(matched.get('keywords', []) or []),
                'Language': enrichments.get('language_code', 'en'),
                
                # Metadata fields
                'Content Type': record.get('content_type', ''),
                'Tweet Id': record.get('external_id', ''),
                'Twitter Id': author.get('external_id', ''),
                'User Profile Url': author.get('profile_url', ''),
                'Hidden': str(record.get('custom', {}).get('hidden', False)),
                
                # Fill remaining fields with defaults to match 36-field schema
                'Summarization Disabled': 'False',
                'Metric Type': '',
                'Metric Category': '',
                'Performance Notes': '',
                'Recommendation': '',
                'Priority': '',
                'Task Status': '',
                'News': '',
                'Press Release': '',
                'Report': '',
                'Social Media': 'Yes' if source.get('type') == 'social network' else 'No',
                'Blog': '',
                'Forum': 'Yes' if source.get('type') == 'forum' else 'No',
                'Media Mention': 'Yes' if source.get('type') == 'online news' else 'No',
            }
            
            transformed_rows.append(row)
            
        except Exception as e:
            # Skip malformed records
            st.warning(f"Skipping malformed Meltwater record: {str(e)}")
            continue
    
    return pd.DataFrame(transformed_rows)


@st.cache_data(ttl=3600)
def load_data(sources: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Load and combine data from multiple CSV and JSON sources.
    
    Args:
        sources: List of source configurations with 'path', 'type', and 'brand'
        
    Returns:
        Combined DataFrame with normalized schema and brand column
    """
    all_dfs = []
    
    for source in sources:
        path = source['path']
        source_type = source['type']
        brand_name = source.get('brand')
        
        try:
            if source_type == 'csv':
                df = pd.read_csv(path)
            elif source_type == 'json':
                # Try direct JSON read first
                try:
                    df = pd.read_json(path)
                except:
                    # Fallback: load as dict and normalize
                    with open(path, 'r') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.json_normalize(data)
            elif source_type == 'meltwater':
                # Load Meltwater API format and transform
                with open(path, 'r', encoding='utf-8') as f:
                    meltwater_data = json.load(f)
                
                # Meltwater data is typically an object with 'documents' array
                if isinstance(meltwater_data, dict) and 'documents' in meltwater_data:
                    df = transform_meltwater_data(meltwater_data['documents'])
                elif isinstance(meltwater_data, list):
                    df = transform_meltwater_data(meltwater_data)
                else:
                    st.warning(f"Unexpected Meltwater format in {path}")
                    continue
            else:
                st.warning(f"Unknown source type: {source_type} for {path}")
                continue
            
            # Normalize column names (strip whitespace, handle case)
            df.columns = df.columns.str.strip()
            
            # Add brand column if not present
            if 'brand' not in df.columns and 'Brand' not in df.columns:
                if brand_name:
                    df['brand'] = brand_name
                else:
                    # Infer from filename
                    filename = Path(path).stem
                    df['brand'] = filename.split(' - ')[0] if ' - ' in filename else filename
            elif 'Brand' in df.columns:
                df.rename(columns={'Brand': 'brand'}, inplace=True)
            
            # If brand_name is specified in config, override
            if brand_name:
                df['brand'] = brand_name
            
            all_dfs.append(df)
            
        except FileNotFoundError:
            st.warning(f"File not found: {path}")
        except Exception as e:
            st.error(f"Error loading {path}: {str(e)}")
    
    if not all_dfs:
        # Return empty DataFrame with expected schema
        return pd.DataFrame(columns=['Date', 'brand', 'Sentiment', 'Source', 'Engagement'])
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    return combined_df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare and clean the data for analysis.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame with computed fields
    """
    if df.empty:
        return df
    
    # Parse Date column
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Add numeric sentiment score
    sentiment_map = {
        'positive': 1,
        'neutral': 0,
        'negative': -1,
        'unknown': 0
    }
    
    if 'Sentiment' in df.columns:
        df['sentiment_score'] = df['Sentiment'].str.lower().map(sentiment_map).fillna(0)
    else:
        df['sentiment_score'] = 0
    
    # Ensure numeric columns
    numeric_cols = ['Reach', 'Engagement', 'Views', 'Estimated Views', 'AVE']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Fill missing values for key columns
    if 'Source' in df.columns:
        df['Source'] = df['Source'].fillna('Unknown')
    
    if 'Country' in df.columns:
        df['Country'] = df['Country'].fillna('Unknown')
    
    return df


def get_brand_list(df: pd.DataFrame) -> List[str]:
    """Extract unique brand names from DataFrame."""
    if 'brand' in df.columns:
        brands = df['brand'].dropna().unique().tolist()
        return sorted(brands) if brands else ['No brands found']
    return ['No brands found']


def compute_metrics(df_brand: pd.DataFrame, df_all: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute key metrics for a specific brand.
    
    Args:
        df_brand: Filtered DataFrame for selected brand
        df_all: Full DataFrame with all brands
        
    Returns:
        Dictionary of computed metrics
    """
    metrics = {}
    
    # Sentiment Index (0-100 scale)
    if len(df_brand) > 0:
        avg_sentiment = df_brand['sentiment_score'].mean()
        metrics['sentiment_index'] = ((avg_sentiment + 1) / 2) * 100
    else:
        metrics['sentiment_index'] = 50
    
    # Share of Voice (%)
    total_mentions = len(df_all)
    brand_mentions = len(df_brand)
    metrics['share_of_voice'] = (brand_mentions / total_mentions * 100) if total_mentions > 0 else 0
    
    # Trend Velocity (% change over last 14 days)
    if 'Date' in df_brand.columns and len(df_brand) > 0:
        today = df_brand['Date'].max()
        last_14_days = df_brand[df_brand['Date'] >= (today - timedelta(days=14))]
        prev_14_days = df_brand[(df_brand['Date'] >= (today - timedelta(days=28))) & 
                                (df_brand['Date'] < (today - timedelta(days=14)))]
        
        recent_engagement = last_14_days['Engagement'].sum() if 'Engagement' in df_brand.columns else len(last_14_days)
        prev_engagement = prev_14_days['Engagement'].sum() if 'Engagement' in df_brand.columns else len(prev_14_days)
        
        if prev_engagement > 0:
            metrics['trend_velocity'] = ((recent_engagement - prev_engagement) / prev_engagement) * 100
        else:
            metrics['trend_velocity'] = 0
    else:
        metrics['trend_velocity'] = 0
    
    # Total Reach
    metrics['total_reach'] = df_brand['Reach'].sum() if 'Reach' in df_brand.columns else 0
    
    # Total Mentions
    metrics['total_mentions'] = len(df_brand)
    
    # Average Engagement
    metrics['avg_engagement'] = df_brand['Engagement'].mean() if 'Engagement' in df_brand.columns and len(df_brand) > 0 else 0
    
    # Marketing Health Score (composite: 0-100)
    # Formula: 0.4 * sentiment_index + 0.3 * normalized_engagement + 0.3 * normalized_reach
    if len(df_brand) > 0:
        max_engagement = df_all['Engagement'].max() if 'Engagement' in df_all.columns else 1
        max_reach = df_all['Reach'].max() if 'Reach' in df_all.columns else 1
        
        norm_engagement = (metrics['avg_engagement'] / max_engagement * 100) if max_engagement > 0 else 0
        norm_reach = (metrics['total_reach'] / max_reach * 100) if max_reach > 0 else 0
        
        metrics['health_score'] = (0.4 * metrics['sentiment_index'] + 
                                   0.3 * norm_engagement + 
                                   0.3 * norm_reach)
    else:
        metrics['health_score'] = 0
    
    return metrics


# ============================================================================
# UI RENDERING FUNCTIONS
# ============================================================================

def render_sidebar(brand_list: List[str]) -> Dict[str, Any]:
    """
    Render sidebar with navigation and filters.
    
    Returns:
        Dictionary of selected filter values
    """
    with st.sidebar:
        st.markdown("<h1 style='text-align: center; margin-left: 0; margin-right: 0;'>Brand ⚡ Surge</h1>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Brand selector - moved above navigation
        st.markdown("### Brand Selection")
        selected_brand = st.selectbox(
            "Select Brand",
            options=brand_list,
            key="brand_selector"
        )
        
        st.markdown("---")
        
        # Navigation (static for now)
        st.markdown("### Navigation")
        nav_items = [
            ("Dashboard", True),
            ("Uplifted Feeds", False),
            ("Campaigns", False),
            ("Orchestration", False),
            ("Metrics & Attribution", False),
            ("Social Agents", False),
            ("Integrations", False),
            ("Security", False)
        ]
        
        for item, active in nav_items:
            if active:
                st.markdown(f'<div class="nav-item active">{item}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="nav-item">• {item}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Date range filter
        st.markdown("### Date Range")
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="date_range"
        )
        
        st.markdown("---")
        st.markdown("*Data updates every hour*")
    
    return {
        'selected_brand': selected_brand,
        'date_range': date_range
    }


def render_kpis(metrics: Dict[str, Any], df_brand: pd.DataFrame):
    """Render top KPI row with gauge visualizations and keywords block."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### Sentiment Index")
        fig_sentiment = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics['sentiment_index'],
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'color': '#f1f5f9', 'size': 32}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#f1f5f9'},
                'bar': {'color': '#10b981'},
                'bgcolor': '#1e293b',
                'borderwidth': 2,
                'bordercolor': '#334155',
                'steps': [
                    {'range': [0, 33], 'color': '#ef4444'},
                    {'range': [33, 66], 'color': '#fbbf24'},
                    {'range': [66, 100], 'color': '#10b981'}
                ],
                'threshold': {
                    'line': {'color': '#f1f5f9', 'width': 4},
                    'thickness': 0.75,
                    'value': metrics['sentiment_index']
                }
            }
        ))
        
        fig_sentiment.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#f1f5f9'},
            height=200,
            margin=dict(l=20, r=20, t=0, b=0)
        )
        
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        st.markdown("#### Trend Velocity")
        # Normalize trend velocity to 0-100 scale for gauge display
        # Map -100% to 100% range to 0-100 gauge scale
        normalized_velocity = min(100, max(0, (metrics['trend_velocity'] + 100) / 2))
        
        fig_velocity = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=metrics['trend_velocity'],
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'suffix': '%', 'font': {'color': '#f1f5f9', 'size': 32}},
            delta={'reference': 0, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#ef4444'}},
            gauge={
                'axis': {'range': [-100, 100], 'tickcolor': '#f1f5f9'},
                'bar': {'color': '#8b5cf6'},
                'bgcolor': '#1e293b',
                'borderwidth': 2,
                'bordercolor': '#334155',
                'steps': [
                    {'range': [-100, -33], 'color': '#ef4444'},
                    {'range': [-33, 33], 'color': '#fbbf24'},
                    {'range': [33, 100], 'color': '#10b981'}
                ],
                'threshold': {
                    'line': {'color': '#f1f5f9', 'width': 4},
                    'thickness': 0.75,
                    'value': metrics['trend_velocity']
                }
            }
        ))
        
        fig_velocity.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#f1f5f9'},
            height=200,
            margin=dict(l=20, r=20, t=0, b=0)
        )
        
        st.plotly_chart(fig_velocity, use_container_width=True)
    
    with col3:
        st.markdown("#### Share of Voice")
        fig_sov = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics['share_of_voice'],
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'suffix': '%', 'font': {'color': '#f1f5f9', 'size': 32}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#f1f5f9'},
                'bar': {'color': '#3b82f6'},
                'bgcolor': '#1e293b',
                'borderwidth': 2,
                'bordercolor': '#334155',
                'steps': [
                    {'range': [0, 25], 'color': '#334155'},
                    {'range': [25, 50], 'color': '#475569'},
                    {'range': [50, 75], 'color': '#64748b'},
                    {'range': [75, 100], 'color': '#94a3b8'}
                ],
                'threshold': {
                    'line': {'color': '#f1f5f9', 'width': 4},
                    'thickness': 0.75,
                    'value': metrics['share_of_voice']
                }
            }
        ))
        
        fig_sov.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#f1f5f9'},
            height=200,
            margin=dict(l=20, r=20, t=0, b=0)
        )
        
        st.plotly_chart(fig_sov, use_container_width=True)
    
    with col4:
        st.markdown("#### Top Keywords")
        
        # Extract keywords
        keywords_list = []
        if len(df_brand) > 0:
            if 'Key Phrases' in df_brand.columns:
                for phrases in df_brand['Key Phrases'].dropna():
                    if isinstance(phrases, str) and phrases:
                        keywords_list.extend([kw.strip().lower() for kw in phrases.replace(';', ',').split(',') if kw.strip()])
            
            if 'Keywords' in df_brand.columns:
                for keywords in df_brand['Keywords'].dropna():
                    if isinstance(keywords, str) and keywords:
                        keywords_list.extend([kw.strip().lower() for kw in keywords.replace(';', ',').split(',') if kw.strip()])
        
        # Display keywords in pastel yellow blocks
        if keywords_list:
            keyword_counts = pd.Series(keywords_list).value_counts().head(8)
            
            # Create HTML for keyword tags
            keywords_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">'
            for keyword in keyword_counts.index:
                keywords_html += f'''<span style="
                    background-color: #fef3c7;
                    color: #78350f;
                    padding: 6px 12px;
                    border-radius: 16px;
                    font-size: 13px;
                    font-weight: 600;
                    display: inline-block;
                    margin: 4px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                ">{keyword}</span>'''
            keywords_html += '</div>'
            
            st.markdown(keywords_html, unsafe_allow_html=True)
        else:
            st.info("No keywords available")


def render_main_charts(df_brand: pd.DataFrame, metric_name: str):
    """Render main charts section with full-width layout."""
    
    # First row: Channel Performance and Geo Sentiment side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Channel Performance")
        
        if len(df_brand) > 0 and 'Source' in df_brand.columns:
            # Map metric name to column
            metric_col_map = {
                'Mentions': None,  # Use count
                'Views': 'Views',
                'Engagement': 'Engagement',
                'Estimated Views': 'Estimated Views'
            }
            
            metric_col = metric_col_map.get(metric_name)
            
            if metric_col and metric_col in df_brand.columns:
                channel_data = df_brand.groupby('Source')[metric_col].sum().reset_index()
                channel_data.columns = ['Source', 'Value']
            else:
                # Count mentions
                channel_data = df_brand.groupby('Source').size().reset_index()
                channel_data.columns = ['Source', 'Value']
            
            channel_data = channel_data.sort_values('Value', ascending=False).head(10)
            
            fig = px.bar(
                channel_data,
                x='Source',
                y='Value',
                title=f'{metric_name} by Channel',
                color='Value',
                color_continuous_scale=['#3b82f6', '#8b5cf6', '#10b981'],
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                showlegend=False,
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor='#334155'),
                yaxis=dict(gridcolor='#334155')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No channel data available")
    
    with col2:
        st.markdown("### Geo Sentiment Heatmap")
        
        if len(df_brand) > 0 and 'Country' in df_brand.columns:
            # Aggregate sentiment by country
            geo_data = df_brand.groupby('Country').agg({
                'sentiment_score': 'mean',
                'Sentiment': 'count'
            }).reset_index()
            geo_data.columns = ['Country', 'Avg_Sentiment', 'Mentions']
            geo_data = geo_data[geo_data['Country'] != 'Unknown'].sort_values('Mentions', ascending=False).head(15)
            
            # Create choropleth-style heatmap
            fig = px.bar(
                geo_data,
                x='Country',
                y='Avg_Sentiment',
                color='Avg_Sentiment',
                title='Average Sentiment by Country',
                color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'],
                color_continuous_midpoint=0,
                hover_data={'Mentions': True}
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                showlegend=False,
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor='#334155', tickangle=45),
                yaxis=dict(gridcolor='#334155')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geographic data available")


def render_keywords_section(df_brand: pd.DataFrame):
    """Render top keywords analysis section."""
    st.markdown("### Top Keywords")
    
    if len(df_brand) > 0:
        # Extract keywords from Key Phrases column
        keywords_list = []
        
        if 'Key Phrases' in df_brand.columns:
            for phrases in df_brand['Key Phrases'].dropna():
                if isinstance(phrases, str) and phrases:
                    # Split by common delimiters
                    keywords_list.extend([kw.strip().lower() for kw in phrases.replace(';', ',').split(',') if kw.strip()])
        
        # Also extract from Keywords column if available
        if 'Keywords' in df_brand.columns:
            for keywords in df_brand['Keywords'].dropna():
                if isinstance(keywords, str) and keywords:
                    keywords_list.extend([kw.strip().lower() for kw in keywords.replace(';', ',').split(',') if kw.strip()])
        
        if keywords_list:
            # Count keyword frequency
            keyword_counts = pd.Series(keywords_list).value_counts().head(20)
            
            # Create horizontal bar chart
            fig_keywords = px.bar(
                x=keyword_counts.values,
                y=keyword_counts.index,
                orientation='h',
                title='Top 20 Keywords by Frequency',
                labels={'x': 'Frequency', 'y': 'Keyword'},
                color=keyword_counts.values,
                color_continuous_scale=['#3b82f6', '#8b5cf6', '#10b981']
            )
            
            fig_keywords.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                showlegend=False,
                height=500,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor='#334155'),
                yaxis=dict(gridcolor='#334155', autorange='reversed')
            )
            
            st.plotly_chart(fig_keywords, use_container_width=True)
            
            # Top 10 keywords table with counts
            st.markdown("#### Top Keywords Summary")
            top_keywords_df = pd.DataFrame({
                'Keyword': keyword_counts.head(10).index,
                'Frequency': keyword_counts.head(10).values
            })
            
            st.dataframe(
                top_keywords_df,
                use_container_width=True,
                hide_index=True,
                height=300
            )
        else:
            st.info("No keyword data available. Make sure 'Key Phrases' or 'Keywords' columns contain data.")
    else:
        st.info("No data available for keyword analysis")


def render_right_sidebar(df_brand: pd.DataFrame, metrics: Dict[str, Any]):
    """Render permanent right sidebar with Live Metrics as a custom section."""
    
    # Build the HTML components
    html_parts = []
    
    # Start with container wrapper
    html_parts.append('<div id="live-metrics-sidebar">')
    
    # Sidebar container with enhanced header
    html_parts.append("""
    <div class="right-sidebar">
        <div style='text-align: center; margin-bottom: 20px;'>
            <h3 style='color: #f1f5f9; font-size: 20px; margin: 0; padding-bottom: 12px; border-bottom: 2px solid #8b5cf6; font-weight: 700; letter-spacing: 0.5px;'>
                📊 LIVE METRICS
            </h3>
        </div>
    """)
    
    # KPIs section with enhanced styling
    html_parts.append(f"""
        <div style='margin-bottom: 24px;'>
            <div style='background: linear-gradient(135deg, #1e293b, #334155); border-radius: 10px; padding: 14px; margin: 10px 0; border-left: 4px solid #10b981; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);'>
                <div style='color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>Total Mentions</div>
                <div style='color: #f1f5f9; font-size: 26px; font-weight: 700;'>{metrics['total_mentions']:,}</div>
            </div>
            <div style='background: linear-gradient(135deg, #1e293b, #334155); border-radius: 10px; padding: 14px; margin: 10px 0; border-left: 4px solid #3b82f6; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);'>
                <div style='color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>Total Reach</div>
                <div style='color: #f1f5f9; font-size: 26px; font-weight: 700;'>{metrics['total_reach']:,.0f}</div>
            </div>
            <div style='background: linear-gradient(135deg, #1e293b, #334155); border-radius: 10px; padding: 14px; margin: 10px 0; border-left: 4px solid #8b5cf6; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);'>
                <div style='color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>Avg Engagement</div>
                <div style='color: #f1f5f9; font-size: 26px; font-weight: 700;'>{metrics['avg_engagement']:,.1f}</div>
            </div>
            <div style='background: linear-gradient(135deg, #1e293b, #334155); border-radius: 10px; padding: 14px; margin: 10px 0; border-left: 4px solid #fbbf24; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);'>
                <div style='color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>Health Score</div>
                <div style='color: #f1f5f9; font-size: 26px; font-weight: 700;'>{metrics['health_score']:.1f}/100</div>
            </div>
        </div>
        <div style='border-top: 2px solid #334155; margin: 24px 0;'></div>
    """)
    
    # Sentiment Distribution
    if len(df_brand) > 0 and 'Sentiment' in df_brand.columns:
        html_parts.append("""
        <div style='margin-bottom: 24px;'>
            <h4 style='color: #f1f5f9; font-size: 14px; margin-bottom: 14px; font-weight: 600; letter-spacing: 0.5px;'>
                🎯 SENTIMENT DISTRIBUTION
            </h4>
            <div style='margin: 10px 0;'>
        """)
        
        sentiment_dist = df_brand['Sentiment'].value_counts()
        total = sentiment_dist.sum()
        colors = {'positive': '#10b981', 'neutral': '#fbbf24', 'negative': '#ef4444', 'unknown': '#94a3b8'}
        
        for sent, count in sentiment_dist.items():
            pct = (count / total * 100) if total > 0 else 0
            color = colors.get(sent, '#94a3b8')
            html_parts.append(f"""
            <div style='margin: 10px 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                    <span style='color: #f1f5f9; font-size: 12px; font-weight: 500;'>{sent.title()}</span>
                    <span style='color: #94a3b8; font-size: 12px; font-weight: 600;'>{pct:.1f}%</span>
                </div>
                <div style='background: #0f172a; border-radius: 6px; height: 8px; overflow: hidden; border: 1px solid #334155;'>
                    <div style='background: {color}; height: 100%; width: {pct}%; transition: width 0.3s ease;'></div>
                </div>
            </div>
            """)
        html_parts.append("</div></div><div style='border-top: 2px solid #334155; margin: 24px 0;'></div>")
    
    # Top Sources
    if len(df_brand) > 0 and 'Source' in df_brand.columns:
        html_parts.append("""
        <div style='margin-bottom: 20px;'>
            <h4 style='color: #f1f5f9; font-size: 14px; margin-bottom: 14px; font-weight: 600; letter-spacing: 0.5px;'>
                📋 TOP SOURCES
            </h4>
            <div style='margin: 10px 0;'>
        """)
        
        top_sources = df_brand['Source'].value_counts().head(5)
        for idx, (source, count) in enumerate(top_sources.items(), 1):
            html_parts.append(f"""
            <div style='color: #f1f5f9; font-size: 12px; margin: 8px 0; padding: 10px; background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(109, 40, 217, 0.1)); border-radius: 8px; border-left: 3px solid #8b5cf6; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);'>
                <span style='color: #8b5cf6; font-weight: 700; font-size: 14px;'>{idx}.</span> 
                <span style='font-weight: 500;'>{source}</span>
                <span style='float: right; color: #10b981; font-weight: 700;'>{count:,}</span>
            </div>
            """)
        html_parts.append("</div></div>")
    
    # Close sidebar div
    html_parts.append("</div>")
    
    # Close container wrapper
    html_parts.append("</div>")
    
    # Join and render with unique key to avoid caching issues
    sidebar_html = ''.join(html_parts)
    st.markdown(sidebar_html, unsafe_allow_html=True)


def render_right_panel(df_brand: pd.DataFrame, metrics: Dict[str, Any]):
    """Render right sidebar with Live Metrics."""
    st.markdown('<div style="position: sticky; top: 20px;">', unsafe_allow_html=True)
    
    st.markdown("### 📊 Live Metrics")
    st.markdown("---")
    
    # Real-time KPIs
    st.markdown("#### KPIs")
    
    st.metric("Total Mentions", f"{metrics['total_mentions']:,}")
    st.metric("Total Reach", f"{metrics['total_reach']:,.0f}")
    st.metric("Avg Engagement", f"{metrics['avg_engagement']:,.1f}")
    st.metric("Health Score", f"{metrics['health_score']:.1f}/100")
    
    st.markdown("---")
    
    # Marketing Health Score Gauge
    st.markdown("#### Health Score")
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=metrics['health_score'],
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'color': '#f1f5f9', 'size': 24}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': '#f1f5f9'},
            'bar': {'color': '#8b5cf6'},
            'bgcolor': '#1e293b',
            'borderwidth': 2,
            'bordercolor': '#334155',
            'steps': [
                {'range': [0, 33], 'color': '#ef4444'},
                {'range': [33, 66], 'color': '#fbbf24'},
                {'range': [66, 100], 'color': '#10b981'}
            ],
            'threshold': {
                'line': {'color': '#f1f5f9', 'width': 4},
                'thickness': 0.75,
                'value': metrics['health_score']
            }
        }
    ))
    
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#f1f5f9'},
        height=180,
        margin=dict(l=5, r=5, t=5, b=5)
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    st.markdown("---")
    
    # 7-Day Engagement Trend
    st.markdown("#### 7-Day Trend")
    
    if len(df_brand) > 0 and 'Date' in df_brand.columns:
        today = df_brand['Date'].max()
        last_7_days = df_brand[df_brand['Date'] >= (today - timedelta(days=7))]
        
        if len(last_7_days) > 0:
            trend_data = last_7_days.groupby('Date')['Engagement'].sum().reset_index() if 'Engagement' in df_brand.columns else last_7_days.groupby('Date').size().reset_index(name='Engagement')
            
            fig_trend = px.line(
                trend_data,
                x='Date',
                y='Engagement',
                markers=True,
                line_shape='spline'
            )
            
            fig_trend.update_traces(line_color='#10b981', marker=dict(size=6, color='#10b981'))
            
            fig_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9', size=10),
                showlegend=False,
                height=150,
                margin=dict(l=5, r=5, t=5, b=5),
                xaxis=dict(gridcolor='#334155', showticklabels=False),
                yaxis=dict(gridcolor='#334155')
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No recent data")
    
    st.markdown("---")
    
    # Sentiment Distribution
    st.markdown("#### Sentiment")
    
    if len(df_brand) > 0 and 'Sentiment' in df_brand.columns:
        sentiment_dist = df_brand['Sentiment'].value_counts()
        
        fig_sentiment_pie = px.pie(
            values=sentiment_dist.values,
            names=sentiment_dist.index,
            color=sentiment_dist.index,
            color_discrete_map={
                'positive': '#10b981',
                'neutral': '#fbbf24',
                'negative': '#ef4444',
                'unknown': '#94a3b8'
            }
        )
        
        fig_sentiment_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', size=10),
            showlegend=True,
            height=180,
            margin=dict(l=5, r=5, t=5, b=5)
        )
        
        st.plotly_chart(fig_sentiment_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Top Sources
    st.markdown("#### Top Sources")
    
    if len(df_brand) > 0 and 'Source' in df_brand.columns:
        top_sources = df_brand['Source'].value_counts().head(5)
        
        for idx, (source, count) in enumerate(top_sources.items(), 1):
            st.markdown(f"**{idx}.** {source}: {count:,}")
    else:
        st.info("No source data")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_recommendations(df_brand: pd.DataFrame, metrics: Dict[str, Any]):
    """Render bottom recommendations panel."""
    st.markdown('<div class="recommendation-panel">', unsafe_allow_html=True)
    st.markdown("### Agentic Recommendations")
    
    # Generate summary text
    if len(df_brand) > 0:
        # Dominant sentiment
        if 'Sentiment' in df_brand.columns:
            sentiment_counts = df_brand['Sentiment'].value_counts()
            dominant_sentiment = sentiment_counts.index[0] if len(sentiment_counts) > 0 else 'neutral'
        else:
            dominant_sentiment = 'neutral'
        
        # Top channel
        if 'Source' in df_brand.columns:
            top_channel = df_brand['Source'].value_counts().index[0] if len(df_brand['Source'].value_counts()) > 0 else 'Unknown'
        else:
            top_channel = 'Unknown'
        
        # Trend direction
        trend_direction = "upward" if metrics['trend_velocity'] > 0 else "downward" if metrics['trend_velocity'] < 0 else "stable"
        
        summary = f"""
        **Current Analysis:** Your brand is experiencing **{dominant_sentiment}** sentiment with a **{trend_direction}** 
        trend ({metrics['trend_velocity']:.1f}% velocity). The primary engagement channel is **{top_channel}** 
        with {metrics['total_mentions']:,} total mentions. Marketing health score is at **{metrics['health_score']:.1f}/100**.
        Consider the recommended actions below to optimize your brand presence.
        """
        
        st.markdown(summary)
    else:
        st.markdown("**No data available for recommendations.**")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Generate Variant", use_container_width=True, type="primary"):
            st.toast("Generating content variant...")
    
    with col2:
        if st.button("Launch Social Agents", use_container_width=True, type="primary"):
            st.toast("Social agents deployed!")
    
    with col3:
        if st.button("Simulate ROI", use_container_width=True, type="primary"):
            st.toast("Running ROI simulation...")
    
    with col4:
        if st.button("Add to Campaign", use_container_width=True, type="primary"):
            st.toast("Added to active campaign!")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Load and prepare data
    with st.spinner("Loading data sources..."):
        df_all = load_data(DATA_SOURCES)
        df_all = prepare_data(df_all)
    
    if df_all.empty:
        st.error("No data loaded. Please check your DATA_SOURCES configuration.")
        st.info("Make sure the CSV/JSON files exist and the paths are correct.")
        return
    
    # Get brand list
    brand_list = get_brand_list(df_all)
    
    # Render sidebar and get filters
    filters = render_sidebar(brand_list)
    
    # Filter data by selected brand
    if filters['selected_brand'] and filters['selected_brand'] != 'No brands found':
        df_brand = df_all[df_all['brand'] == filters['selected_brand']].copy()
    else:
        df_brand = df_all.copy()
    
    # Apply date filter
    if 'Date' in df_brand.columns and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        df_brand = df_brand[(df_brand['Date'] >= pd.Timestamp(start_date)) & 
                           (df_brand['Date'] <= pd.Timestamp(end_date))]
    
    # Compute metrics
    metrics = compute_metrics(df_brand, df_all)
    
    # Main layout
    st.markdown("# Brand Analytics Dashboard")
    st.markdown(f"### {filters['selected_brand']}")
    st.markdown("---")
    
    # Top KPI row with keywords
    render_kpis(metrics, df_brand)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main charts section - Enhanced Channel Performance
    st.markdown("---")
    st.markdown("### 📈 Performance Overview")
    
    # First row - Channel Performance Metrics (2 columns)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Channel Mentions & Engagement")
        
        if len(df_brand) > 0 and 'Source' in df_brand.columns:
            # Aggregate data by channel
            channel_data = df_brand.groupby('Source').agg({
                'Sentiment': 'count',  # Mentions
                'Engagement': 'sum' if 'Engagement' in df_brand.columns else 'count'
            }).reset_index()
            channel_data.columns = ['Channel', 'Mentions', 'Total_Engagement']
            channel_data = channel_data.sort_values('Mentions', ascending=False).head(10)
            
            # Create grouped bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Mentions',
                x=channel_data['Channel'],
                y=channel_data['Mentions'],
                marker_color='#8b5cf6',
                text=channel_data['Mentions'],
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                name='Total Engagement',
                x=channel_data['Channel'],
                y=channel_data['Total_Engagement'],
                marker_color='#3b82f6',
                text=channel_data['Total_Engagement'].apply(lambda x: f'{x:,.0f}'),
                textposition='auto',
                yaxis='y2'
            ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor='#334155', title='Channel'),
                yaxis=dict(gridcolor='#334155', title='Mentions', side='left'),
                yaxis2=dict(gridcolor='#334155', title='Total Engagement', side='right', overlaying='y'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No channel data available")
    
    with col2:
        st.markdown("#### Channel Reach & Views")
        
        if len(df_brand) > 0 and 'Source' in df_brand.columns:
            # Aggregate reach and views by channel
            channel_reach = df_brand.groupby('Source').agg({
                'Reach': 'sum' if 'Reach' in df_brand.columns else 'count',
                'Views': 'sum' if 'Views' in df_brand.columns else 'count'
            }).reset_index()
            channel_reach.columns = ['Channel', 'Total_Reach', 'Total_Views']
            channel_reach = channel_reach.sort_values('Total_Reach', ascending=False).head(10)
            
            # Create grouped bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Total Reach',
                x=channel_reach['Channel'],
                y=channel_reach['Total_Reach'],
                marker_color='#10b981',
                text=channel_reach['Total_Reach'].apply(lambda x: f'{x:,.0f}'),
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                name='Total Views',
                x=channel_reach['Channel'],
                y=channel_reach['Total_Views'],
                marker_color='#fbbf24',
                text=channel_reach['Total_Views'].apply(lambda x: f'{x:,.0f}'),
                textposition='auto'
            ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor='#334155', title='Channel'),
                yaxis=dict(gridcolor='#334155', title='Count'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No channel data available")
    
    # Second row - Geographic Sentiment (full width)
    st.markdown("#### Geographic Sentiment Distribution")
    
    if len(df_brand) > 0 and 'Country' in df_brand.columns:
        geo_data = df_brand.groupby('Country').agg({
            'sentiment_score': 'mean',
            'Sentiment': 'count'
        }).reset_index()
        geo_data.columns = ['Country', 'Avg_Sentiment', 'Mentions']
        geo_data = geo_data[geo_data['Country'] != 'Unknown'].sort_values('Mentions', ascending=False).head(15)
        
        fig = px.bar(
            geo_data,
            x='Country',
            y='Avg_Sentiment',
            color='Avg_Sentiment',
            title='Average Sentiment by Country',
            color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'],
            color_continuous_midpoint=0,
            hover_data={'Mentions': True}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9'),
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(gridcolor='#334155', tickangle=45),
            yaxis=dict(gridcolor='#334155')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No geographic data available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Live Metrics Section
    st.markdown("### 📊 Live Metrics")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Real-time KPIs")
        st.metric("Total Mentions", f"{metrics['total_mentions']:,}")
        st.metric("Total Reach", f"{metrics['total_reach']:,.0f}")
        st.metric("Avg Engagement", f"{metrics['avg_engagement']:,.1f}")
        st.metric("Health Score", f"{metrics['health_score']:.1f}/100")
    
    with col2:
        st.markdown("#### Sentiment Distribution")
        if len(df_brand) > 0 and 'Sentiment' in df_brand.columns:
            sentiment_dist = df_brand['Sentiment'].value_counts()
            fig_sentiment = go.Figure(data=[go.Pie(
                labels=sentiment_dist.index,
                values=sentiment_dist.values,
                hole=0.4,
                marker=dict(colors=['#10b981', '#fbbf24', '#ef4444', '#94a3b8'])
            )])
            fig_sentiment.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9'),
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True
            )
            st.plotly_chart(fig_sentiment, use_container_width=True, key="live_sentiment")
    
    with col3:
        st.markdown("#### Top Sources")
        if len(df_brand) > 0 and 'Source' in df_brand.columns:
            top_sources = df_brand['Source'].value_counts().head(5)
            for idx, (source, count) in enumerate(top_sources.items(), 1):
                st.markdown(f"**{idx}. {source}:** {count:,} mentions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Channel Metrics Table - under Live Metrics
    st.markdown("### Detailed Channel Metrics")
    
    if len(df_brand) > 0 and 'Source' in df_brand.columns:
        channel_metrics = df_brand.groupby('Source').agg({
            'Sentiment': 'count',
            'Engagement': 'sum' if 'Engagement' in df_brand.columns else 'count',
            'Views': 'sum' if 'Views' in df_brand.columns else 'count',
            'Reach': 'sum' if 'Reach' in df_brand.columns else 'count',
            'sentiment_score': 'mean'
        }).reset_index()
        
        channel_metrics.columns = ['Channel', 'Mentions', 'Engagement', 'Views', 'Reach', 'Avg Sentiment']
        channel_metrics = channel_metrics.sort_values('Mentions', ascending=False).head(10)
        
        channel_metrics['Engagement'] = channel_metrics['Engagement'].apply(lambda x: f"{x:,.0f}")
        channel_metrics['Views'] = channel_metrics['Views'].apply(lambda x: f"{x:,.0f}")
        channel_metrics['Reach'] = channel_metrics['Reach'].apply(lambda x: f"{x:,.0f}")
        channel_metrics['Avg Sentiment'] = channel_metrics['Avg Sentiment'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(
            channel_metrics,
            use_container_width=True,
            hide_index=True,
            height=350
        )
    else:
        st.info("No channel data available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Agentic Recommendations - Simple section without purple bubble
    st.markdown("### Agentic Recommendations")
    st.markdown("---")
    
    if len(df_brand) > 0:
        # Dominant sentiment
        if 'Sentiment' in df_brand.columns:
            sentiment_counts = df_brand['Sentiment'].value_counts()
            dominant_sentiment = sentiment_counts.index[0] if len(sentiment_counts) > 0 else 'neutral'
        else:
            dominant_sentiment = 'neutral'
        
        # Top channel
        if 'Source' in df_brand.columns:
            top_channel = df_brand['Source'].value_counts().index[0] if len(df_brand['Source'].value_counts()) > 0 else 'Unknown'
        else:
            top_channel = 'Unknown'
        
        # Trend direction
        trend_direction = "upward" if metrics['trend_velocity'] > 0 else "downward" if metrics['trend_velocity'] < 0 else "stable"
        
        summary = f"""
        **Current Analysis:** Your brand is experiencing **{dominant_sentiment}** sentiment with a **{trend_direction}** 
        trend ({metrics['trend_velocity']:.1f}% velocity). The primary engagement channel is **{top_channel}** 
        with {metrics['total_mentions']:,} total mentions. Marketing health score is at **{metrics['health_score']:.1f}/100**.
        """
        
        st.markdown(summary)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Generate Variant", use_container_width=True, type="primary"):
                st.toast("Generating content variant...")
        
        with col2:
            if st.button("Launch Social Agents", use_container_width=True, type="primary"):
                st.toast("Social agents deployed!")
        
        with col3:
            if st.button("Simulate ROI", use_container_width=True, type="primary"):
                st.toast("Running ROI simulation...")
        
        with col4:
            if st.button("Add to Campaign", use_container_width=True, type="primary"):
                st.toast("Added to active campaign!")
    else:
        st.markdown("**No data available for recommendations.**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Total records: {len(df_all):,} | "
        f"Filtered records: {len(df_brand):,}*"
    )


if __name__ == "__main__":
    main()
