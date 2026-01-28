import requests
import feedparser
import pandas as pd
from datetime import datetime
import os
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

QUERIES = [
    "IPO India",
    "upcoming IPO India",
    "IPO opens for subscription",
    "DRHP SEBI",
    "grey market IPO",
    "mainboard IPO India",
]

rows = []
seen_urls = set()

session = requests.Session()
session.headers.update(HEADERS)

for query in QUERIES:
    encoded = quote_plus(query)

    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    print(f"\nFetching RSS for: {query}")

    rss_resp = session.get(rss_url, timeout=15)
    feed = feedparser.parse(rss_resp.text)

    print("RSS entries:", len(feed.entries))

    for entry in feed.entries:
        link = entry.link

        if link in seen_urls:
            continue

        rows.append({
            "source": "google-news",
            "query": query,
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "url": link,
            "published": entry.get("published", ""),
            "scraped_at": datetime.utcnow().isoformat()
        })

        seen_urls.add(link)

df = pd.DataFrame(rows)

os.makedirs("data/raw", exist_ok=True)
out_path = "data/raw/google_news_metadata.csv"
df.to_csv(out_path, index=False)

print("\n==============================")
print(f"Saved {len(df)} records to {out_path}")
print("==============================")
