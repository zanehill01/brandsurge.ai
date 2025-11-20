# JSON Data Files

Place all your JSON data files in this directory.

## 📋 Expected Format

Your JSON files should be an array of objects with these fields:

```json
[
  {
    "Date": "2025-11-15",
    "Headline": "Product Launch Announcement",
    "URL": "https://example.com/article",
    "Opening Text": "Company announces new product line",
    "Hit Sentence": "Revolutionary new technology",
    "Source": "Twitter",
    "Influencer": "@TechInfluencer",
    "Country": "USA",
    "Subregion": "North America",
    "State": "California",
    "City": "San Francisco",
    "Language": "English",
    "Reach": 100000,
    "Desktop Reach": 50000,
    "Mobile Reach": 50000,
    "Twitter Social Echo": 5000,
    "Facebook Social Echo": 2000,
    "Reddit Social Echo": 800,
    "Earned Traffic": 10000,
    "National Viewership": 0,
    "AVE": 25000,
    "Sentiment": "positive",
    "Key Phrases": "innovation, technology, product launch",
    "Input Name": "Brand Monitoring",
    "Keywords": "product, launch, tech",
    "Document Tags": "product, technology",
    "Engagement": 8000,
    "Hashtags": "#ProductLaunch #Innovation",
    "Views": 50000,
    "Estimated Views": 55000,
    "Custom Categories": "Product Launch",
    "brand": "Your Brand Name"
  }
]
```

## 🔧 Configuration

After adding a JSON file, update `DATA_SOURCES` in `app.py`:

```python
{
    "path": f"{JSON_DIR}/your-file.json",
    "type": "json",
    "brand": "Your Brand Name"  # Or None to use brand from data
}
```

## 📝 Minimum Required Fields

At minimum, your JSON objects should have:
- `Date` - Publication date (YYYY-MM-DD format)
- `Sentiment` - positive/neutral/negative/unknown
- `Source` - Channel (Twitter, News, Blog, etc.)
- `Engagement` or `Views` or `Reach` - Numeric metrics

## 💡 Tips

- Use ISO date format: "2025-11-15"
- Sentiment values must be: "positive", "neutral", "negative", or "unknown"
- Numeric fields should be numbers, not strings
- The `brand` field is optional - can be set in config instead
- Multi-brand JSON: Include different brand names in the `brand` field

## 📚 Sample Files

Check the sample files in this directory:
- `nike_sample.json` - Example Nike brand data
- `adidas_sample.json` - Example Adidas brand data

Use these as templates for your own data files.
