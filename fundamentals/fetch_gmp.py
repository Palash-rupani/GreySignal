"""
GMP Scraper — Option C (ipowatch.in)
Run: python fundamentals/fetch_gmp.py
Output: data/raw/gmp_data.csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os

OUTPUT_PATH = "data/raw/gmp_data.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def parse_gmp_value(text):
    """Extract numeric GMP value from strings like '₹120', '+120', '-50', '120 (15%)'"""
    if not text or text.strip() in ["-", "N/A", ""]:
        return None
    text = text.strip().replace("₹", "").replace(",", "")
    # Extract first number (possibly negative)
    match = re.search(r"-?\d+\.?\d*", text)
    return float(match.group()) if match else None


def parse_percent(text):
    """Extract percentage from strings like '15%', '+15.2%'"""
    if not text:
        return None
    match = re.search(r"-?\d+\.?\d*", str(text))
    return float(match.group()) if match else None


def scrape_ipowatch():
    """Try ipowatch.in GMP table"""
    url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
    print(f"  Trying ipowatch.in...")

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"  Status: {r.status_code}")
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        print(f"  Tables found: {len(tables)}")

        if not tables:
            return None

        results = []
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            # Get headers
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
            print(f"  Headers: {headers}")

            for row in rows[1:]:
                cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cols) < 2:
                    continue

                # Try to identify columns by header
                entry = {}
                for i, h in enumerate(headers):
                    if i >= len(cols):
                        break
                    if any(k in h for k in ["name", "ipo"]):
                        entry["ipo_name"] = cols[i]
                    elif "gmp" in h:
                        entry["gmp"] = parse_gmp_value(cols[i])
                    elif "%" in h or "gain" in h or "return" in h:
                        entry["gmp_percent"] = parse_percent(cols[i])
                    elif "price" in h and "issue" in h:
                        entry["issue_price"] = parse_gmp_value(cols[i])
                    elif "kostak" in h:
                        entry["kostak"] = parse_gmp_value(cols[i])
                    elif "status" in h or "listing" in h:
                        entry["listing_status"] = cols[i]

                # Fallback: use positional if no headers matched
                if not entry.get("ipo_name") and cols:
                    entry["ipo_name"] = cols[0]
                    if len(cols) > 1:
                        entry["gmp"] = parse_gmp_value(cols[1])
                    if len(cols) > 2:
                        entry["gmp_percent"] = parse_percent(cols[2])

                if entry.get("ipo_name") and len(entry["ipo_name"]) > 3:
                    results.append(entry)

        return results if results else None

    except Exception as e:
        print(f"  ipowatch failed: {e}")
        return None


def scrape_chittorgarh():
    """Try chittorgarh.com GMP page"""
    url = "https://www.chittorgarh.com/report/ipo-gmp-grey-market-premium-today-live/95/"
    print(f"  Trying chittorgarh.com...")

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"  Status: {r.status_code}")
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        print(f"  Tables found: {len(tables)}")

        if not tables:
            return None

        results = []
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
            print(f"  Headers: {headers}")

            for row in rows[1:]:
                cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cols) < 2:
                    continue

                entry = {}
                for i, h in enumerate(headers):
                    if i >= len(cols):
                        break
                    if any(k in h for k in ["name", "ipo", "company"]):
                        entry["ipo_name"] = cols[i]
                    elif "gmp" in h:
                        entry["gmp"] = parse_gmp_value(cols[i])
                    elif "%" in h or "est" in h:
                        entry["gmp_percent"] = parse_percent(cols[i])
                    elif "price" in h:
                        entry["issue_price"] = parse_gmp_value(cols[i])
                    elif "subject" in h or "lot" in h:
                        entry["lot_size"] = parse_gmp_value(cols[i])

                if not entry.get("ipo_name") and cols:
                    entry["ipo_name"] = cols[0]
                    if len(cols) > 2:
                        entry["gmp"] = parse_gmp_value(cols[2])

                if entry.get("ipo_name") and len(entry["ipo_name"]) > 3:
                    results.append(entry)

        return results if results else None

    except Exception as e:
        print(f"  Chittorgarh failed: {e}")
        return None


def main():
    print("=" * 50)
    print("GMP Scraper")
    print("=" * 50)

    results = None

    # Try ipowatch first
    results = scrape_ipowatch()
    if results:
        print(f"\n✅ ipowatch.in worked! Found {len(results)} entries")
    else:
        # Fall back to chittorgarh
        print("\n  ipowatch failed, trying chittorgarh...")
        time.sleep(1)
        results = scrape_chittorgarh()
        if results:
            print(f"\n✅ Chittorgarh worked! Found {len(results)} entries")

    if not results:
        print("\n❌ Both sources failed — site may be JS-rendered")
        print("   Try Option A: pip install selenium webdriver-manager")
        return

    # Build DataFrame
    df = pd.DataFrame(results)

    # Clean up name
    df["ipo_name"] = df["ipo_name"].str.strip()

    # Remove junk rows
    junk = ["ipo name", "company", "name", "s.no", "#"]
    df = df[~df["ipo_name"].str.lower().isin(junk)]
    df = df[df["ipo_name"].str.len() > 3]

    # Add timestamp
    df["scraped_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")

    # Ensure output folder exists
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n📋 Sample output:")
    print(df.head(10).to_string(index=False))
    print(f"\n✅ Saved to {OUTPUT_PATH}")
    print(f"   Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()