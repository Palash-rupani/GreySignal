import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time
from urllib.parse import urljoin

session = requests.Session()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

BASE_URL = "https://www.business-standard.com/markets/ipos"

rows = []
seen_urls = set()  # ← deduplication

print("Fetching Business Standard IPO page...")

resp = session.get(BASE_URL, headers=HEADERS, timeout=20)

if resp.status_code != 200:
    print("Blocked on main page, status:", resp.status_code)
    exit()

soup = BeautifulSoup(resp.text, "html.parser")

links = set()

for a in soup.select("a[href]"):
    href = a["href"]
    if "ipo" in href.lower():
        full_url = urljoin("https://www.business-standard.com", href)
        # Only article links, skip section/nav links
        if "/article/" in full_url or "/story/" in full_url or "/news/" in full_url:
            links.add(full_url)

print(f"Found {len(links)} candidate article links.")

for i, link in enumerate(links):
    if link in seen_urls:
        continue

    try:
        print(f"[{i+1}/{len(links)}] Scraping: {link[:80]}")
        article_resp = session.get(link, headers=HEADERS, timeout=20)

        if article_resp.status_code != 200:
            print(f"  Skipped (status {article_resp.status_code})")
            continue

        article_soup = BeautifulSoup(article_resp.text, "html.parser")

        title = article_soup.find("h1")
        title_text = title.get_text(strip=True) if title else ""

        # Get published date if available
        date_tag = article_soup.find("meta", {"property": "article:published_time"})
        published = date_tag["content"] if date_tag and date_tag.get("content") else ""

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in article_soup.find_all("p")
        ]
        text = " ".join(paragraphs)

        if len(text) < 300:
            print("  Skipped (too short)")
            continue

        rows.append({
            "source":     "business-standard",
            "title":      title_text,
            "url":        link,
            "published":  published,
            "text":       text,
            "scraped_at": datetime.utcnow().isoformat()
        })

        seen_urls.add(link)
        time.sleep(1)  # ← polite delay, avoids getting blocked

    except Exception as e:
        print(f"  Failed: {e}")
        time.sleep(1)

df = pd.DataFrame(rows)
os.makedirs("data/raw", exist_ok=True)
out_path = "data/raw/business_standard_articles.csv"
df.to_csv(out_path, index=False)

print(f"\nSaved {len(df)} articles to {out_path}")