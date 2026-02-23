import requests
import feedparser
import pandas as pd
from datetime import datetime
import os
import time
from urllib.parse import quote_plus

# ── Headers ────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# ── IPO-related search queries ─────────────────────────────────────────────
QUERIES = [
    "IPO India",
    "upcoming IPO India",
    "IPO opens for subscription",
    "DRHP SEBI",
    "grey market IPO",
    "mainboard IPO India",
    "SME IPO India",
    "IPO GMP today",
    "IPO allotment India",
]

rows = []
seen_urls = set()

session = requests.Session()
session.headers.update(HEADERS)

# ── RSS Collection ─────────────────────────────────────────────────────────
for query in QUERIES:
    encoded = quote_plus(query)

    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    print(f"\nFetching RSS for: '{query}'")

    try:
        rss_resp = session.get(rss_url, timeout=15)
        feed = feedparser.parse(rss_resp.text)
        print(f"  Found {len(feed.entries)} entries")
    except Exception as e:
        print(f"  Failed to fetch RSS: {e}")
        continue

    for entry in feed.entries:
        link = entry.link

        # Remove duplicates
        if link in seen_urls:
            continue
        seen_urls.add(link)

        rows.append({
            "source": "google-news",
            "query": query,
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "url": link,
            "published": entry.get("published", ""),
            "full_text": "",  # filled below
            "scraped_at": datetime.utcnow().isoformat()
        })

    time.sleep(0.5)  # polite delay between queries

# ── TEXT PREPARATION (FIXED — NO SCRAPING) ─────────────────────────────────
print(f"\nPreparing text for {len(rows)} articles...")

for i, row in enumerate(rows):
    combined = f"{row['title']} {row['summary']}"
    row["full_text"] = combined.strip()

# ── Save to CSV ────────────────────────────────────────────────────────────
df = pd.DataFrame(rows)

os.makedirs("data/raw", exist_ok=True)
out_path = "data/raw/google_news_metadata.csv"

df.to_csv(out_path, index=False)

# ── Final Report ───────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print(f"Saved {len(df)} records to {out_path}")
print(f"Articles with text: {(df['full_text'].str.len() > 20).sum()}")
print("=" * 50)