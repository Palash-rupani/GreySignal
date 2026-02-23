import requests
import pandas as pd
import time
import re

OUT_PATH = "data/processed/ipo_fundamentals_basic.csv"

# NSE needs these headers or it rejects requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

# ── NSE Session (required — NSE needs a cookie first) ────────────────────────
def get_nse_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    # Hit the main page first to get cookies
    session.get("https://www.nseindia.com", timeout=10)
    time.sleep(1)
    return session


def fetch_nse_ipo_list(session: requests.Session) -> pd.DataFrame:
    """Fetch all IPOs from NSE's IPO API."""
    url = "https://www.nseindia.com/api/ipo-current-allotment"
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return pd.DataFrame(data)
    except:
        pass

    # Fallback: broader IPO endpoint
    url2 = "https://www.nseindia.com/api/ipo?category=ipo"
    try:
        r = session.get(url2, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                for key in data:
                    if isinstance(data[key], list):
                        return pd.DataFrame(data[key])
    except:
        pass

    return pd.DataFrame()


def fuzzy_match(ipo_name: str, nse_names: list) -> str | None:
    """Find best matching NSE company name for our IPO name."""
    ipo_lower = ipo_name.lower()

    # Exact match first
    for name in nse_names:
        if ipo_lower == name.lower():
            return name

    # First word match (e.g. "Shadowfax" matches "Shadowfax Technologies Limited")
    first_word = ipo_lower.split()[0]
    for name in nse_names:
        if first_word in name.lower():
            return name

    # All words present
    words = [w for w in ipo_lower.split() if len(w) > 3]
    for name in nse_names:
        name_lower = name.lower()
        if all(w in name_lower for w in words):
            return name

    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Load your IPO names
    try:
        sentiment_df = pd.read_csv("data/processed/ipo_sentiment_summary.csv")
        IPO_LIST = sentiment_df["ipo_name"].dropna().unique().tolist()
        print(f"Loaded {len(IPO_LIST)} IPOs from sentiment summary")
    except FileNotFoundError:
        print("Could not find ipo_sentiment_summary.csv")
        return

    print("Connecting to NSE API...")
    session = get_nse_session()

    nse_df = fetch_nse_ipo_list(session)

    if nse_df.empty:
        print("NSE API returned no data — printing raw response for debug:")
        r = session.get("https://www.nseindia.com/api/ipo?category=ipo", timeout=10)
        print("Status:", r.status_code)
        print("Response preview:", r.text[:500])
    else:
        print(f"NSE returned {len(nse_df)} IPO records")
        print("Columns:", nse_df.columns.tolist())
        print(nse_df.head(3).to_string())

    # ── Also load your manually filled CSV if it exists ───────────────────────
    manual_path = "data/processed/ipo_fundamentals_manual.csv"
    try:
        manual_df = pd.read_csv(manual_path)
        print(f"\nLoaded {len(manual_df)} manually entered IPOs from {manual_path}")
    except FileNotFoundError:
        manual_df = pd.DataFrame()
        print(f"\nNo manual CSV found at {manual_path}")
        print("You can create one using the template below.")

    # ── Print manual template for the most important IPOs ─────────────────────
    # These are your highest article-count IPOs that are worth filling manually
    TOP_IPOS = [
        "Bharat Coking Coal", "Shadowfax Technologies", "PhonePe",
        "Amagi Media Labs", "Groww", "Meesho", "Pine Labs",
        "PhysicsWallah", "ICICI Prudential AMC", "KRM Ayurveda",
    ]

    print("\n" + "="*60)
    print("MANUAL TEMPLATE — copy this to ipo_fundamentals_manual.csv")
    print("Fill in from: https://ipowatch.in or https://chittorgarh.com")
    print("="*60)
    print("ipo_name,issue_size_cr,price_band_low,price_band_high,lot_size,issue_type,exchange,open_date,close_date,listing_date")
    for ipo in TOP_IPOS:
        print(f"{ipo},,,,,,,,," )


if __name__ == "__main__":
    main()
