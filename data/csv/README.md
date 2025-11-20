# CSV Data Files

Place all your CSV data files in this directory.

## 📋 Expected Format

Your CSV files should include these columns:

```csv
Date,Headline,URL,Opening Text,Hit Sentence,Source,Influencer,Country,Subregion,State,City,Language,Reach,Desktop Reach,Mobile Reach,Twitter Social Echo,Facebook Social Echo,Reddit Social Echo,Earned Traffic,National Viewership,AVE,Sentiment,Key Phrases,Input Name,Keywords,Document Tags,Engagement,Hashtags,Views,Estimated Views,Custom Categories
2025-11-15,Product Launch,https://example.com,Product announcement...,Innovative new product,Twitter,@Influencer,USA,North America,California,San Francisco,English,10000,5000,5000,1000,500,200,2000,0,5000,positive,innovation product launch,Brand Monitoring,product launch,product,1500,#Launch,5000,5500,Product
```

## 🔧 Configuration

After adding a CSV file, update `DATA_SOURCES` in `app.py`:

```python
{
    "path": f"{CSV_DIR}/your-file.csv",
    "type": "csv",
    "brand": "Your Brand Name"
}
```

## 📝 Minimum Required Columns

At minimum, your CSV should have:
- `Date`
- `Sentiment` (positive/neutral/negative/unknown)
- `Source` (Twitter, News, Blog, etc.)
- `Engagement` or `Views` or `Reach`

## 💡 Tips

- Date format: YYYY-MM-DD or MM/DD/YYYY
- Sentiment values: positive, neutral, negative, unknown
- Numeric columns (Reach, Engagement, Views) should be numbers without commas
- Brand column is optional - will be added from config if missing
