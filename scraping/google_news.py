"""
scraping/google_news.py

Step 1: Auto-discover current/upcoming IPOs from Chittorgarh + jugaad-data
Step 2: Search Google News for each IPO specifically
Step 3: Broad queries to catch anything missed
"""

import requests
import feedparser
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
from urllib.parse import quote_plus
import re 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BROAD_QUERIES = [
    "IPO India 2025 2026",
    "upcoming IPO India",
    "IPO opens for subscription",
    "DRHP SEBI filed",
    "grey market premium IPO",
    "mainboard IPO India",
    "SME IPO India",
    "IPO GMP today",
    "IPO allotment India",
    "IPO listing date India",
]

rows = []
seen_urls = set()
session = requests.Session()
session.headers.update(HEADERS)


# ── Source 1: Chittorgarh ─────────────────────────────────────────────────────
def fetch_from_chittorgarh() -> list:
    ipo_names = []
    url = "https://www.chittorgarh.com/report/ipo-in-india-list-main-board-sme/82/"

    try:
        r = session.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"  Chittorgarh returned {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")

        # ONLY grab links that point to actual IPO detail pages
        # These look like: /ipo/company-name-ipo/123/
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            # Must match the pattern /ipo/something-ipo/NUMBER/
            import re
            if not re.search(r"/ipo/[\w-]+-ipo/\d+/", href):
                continue

            name = (text
                    .replace(" IPO", "")
                    .replace(" Limited", "")
                    .replace(" Ltd", "")
                    .replace(" Ltd.", "")
                    .strip())

            if len(name) > 4 and name not in ipo_names:
                ipo_names.append(name)

        print(f"  Chittorgarh: found {len(ipo_names)} IPO names")

    except Exception as e:
        print(f"  Chittorgarh error: {e}")

    return ipo_names[:60]

# ── Source 2: jugaad-data (NSE Live) ─────────────────────────────────────────
def fetch_from_jugaad() -> list:
    ipo_names = []

    try:
        from jugaad_data.nse import NSELive
        n = NSELive()

        # Try different possible method names
        data = None
        for method in ("ipo_live", "live_ipo", "ipo"):
            if hasattr(n, method):
                data = getattr(n, method)()
                break

        if data is None:
            print("  jugaad-data: no valid IPO method found")
            return []

        if isinstance(data, list):
            for item in data:
                name = (
                    item.get("companyName")
                    or item.get("name")
                    or item.get("symbol", "")
                )
                name = (
                    str(name)
                    .replace(" Limited", "")
                    .replace(" Ltd", "")
                    .replace(" Ltd.", "")
                    .strip()
                )

                if name and len(name) > 3 and name not in ipo_names:
                    ipo_names.append(name)

        print(f"  jugaad-data NSELive: found {len(ipo_names)} IPO names")

    except ImportError:
        print("  jugaad-data not installed — run: pip install jugaad-data")
    except Exception as e:
        print(f"  jugaad-data error: {e}")

    return ipo_names


# ── Source 3: ipowatch.in fallback ───────────────────────────────────────────
def fetch_from_ipowatch() -> list:
    ipo_names = []

    try:
        r = session.get("https://ipowatch.in/upcoming-ipo-list/", headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]

            # Only grab links that look like actual IPO pages
            # ipowatch URLs look like: /gaudium-ivf-ipo/ or /bharat-coking-coal-ipo/
            if not re.search(r"/[\w-]+-ipo/?$", href):
                continue

            name = (text
                    .replace(" IPO", "")
                    .replace(" Limited", "")
                    .replace(" Ltd", "")
                    .strip())

            # Must look like a company name — title case, no generic words
            junk = {"apply", "upcoming", "gmp", "review", "forms", "listing",
                    "allotment", "subscription", "status", "mainboard", "sme",
                    "ncd", "buyback", "ofs", "rights", "gold", "silver",
                    "performance", "pricing", "tips", "biggests", "what",
                    "how", "importance", "shareholders", "government", "bonus",
                    "stock", "dividend", "matrimony", "tata", "reliance",
                    "adani", "power", "indigrid", "finance"}

            if (len(name) > 4
                    and len(name) < 50
                    and name.lower() not in junk
                    and name not in ipo_names
                    and name[0].isupper()):
                ipo_names.append(name)

        print(f"  ipowatch.in: found {len(ipo_names)} IPO names")

    except Exception as e:
        print(f"  ipowatch.in error: {e}")

    return ipo_names[:60]


# ── Combine & deduplicate IPO names from all sources ─────────────────────────
def discover_ipos() -> list:
    all_names = []
    seen = set()

    for source_fn in [fetch_from_chittorgarh, fetch_from_jugaad, fetch_from_ipowatch]:
        names = source_fn()
        for name in names:
            if name.lower() not in seen:
                seen.add(name.lower())
                all_names.append(name)

    return all_names


# ── RSS fetcher ───────────────────────────────────────────────────────────────
def fetch_rss(query: str, ipo_hint: str = "") -> int:
    encoded = quote_plus(query)
    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    try:
        resp = session.get(rss_url, timeout=15)
        feed = feedparser.parse(resp.text)
        added = 0

        for entry in feed.entries:
            link = entry.link
            if link in seen_urls:
                continue
            seen_urls.add(link)

            title   = entry.title
            summary = entry.get("summary", "")

            rows.append({
                "source":     "google-news",
                "query":      query,
                "ipo_hint":   ipo_hint,
                "title":      title,
                "summary":    summary,
                "full_text":  (title + " " + summary).strip(),
                "url":        link,
                "published":  entry.get("published", ""),
                "scraped_at": datetime.utcnow().isoformat()
            })
            added += 1

        return added

    except Exception as e:
        print(f"  RSS error '{query}': {e}")
        return 0


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Step 1: Discover IPOs
    print("Step 1: Discovering current IPOs from all sources...")
    ipo_names = discover_ipos()

    if ipo_names:
        print(f"\n  Total unique IPOs discovered: {len(ipo_names)}")
        print(f"  Sample: {ipo_names[:5]}")
    else:
        print("  No IPOs discovered — will rely on broad queries only")

    # Step 2: Company-specific searches
    print(f"\nStep 2: Fetching targeted news for {len(ipo_names)} IPOs...")
    for i, name in enumerate(ipo_names):
        query = f"{name} IPO India"
        count = fetch_rss(query, ipo_hint=name)
        print(f"  [{i+1}/{len(ipo_names)}] {name} → {count} new articles")
        time.sleep(0.5)

    # Step 3: Broad queries
    print(f"\nStep 3: Running {len(BROAD_QUERIES)} broad queries...")
    for query in BROAD_QUERIES:
        count = fetch_rss(query)
        print(f"  '{query}' → {count} new articles")
        time.sleep(0.5)

    # Save
    df = pd.DataFrame(rows)
    os.makedirs("data/raw", exist_ok=True)
    out_path = "data/raw/google_news_metadata.csv"
    df.to_csv(out_path, index=False)

    print(f"\n{'='*50}")
    print(f"Total articles:  {len(df)}")
    print(f"IPOs searched:   {len(ipo_names)}")
    print(f"Saved to:        {out_path}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()