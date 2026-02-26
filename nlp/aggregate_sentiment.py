import pandas as pd
from rapidfuzz import process, fuzz

INPUT_PATH   = "data/processed/ipo_sentiment_scored.csv"
SUMMARY_PATH = "data/processed/ipo_sentiment_summary.csv"
TREND_PATH   = "data/processed/ipo_sentiment_trend.csv"

# ── Known junk names to drop before anything else ────────────────────────────
JUNK_NAMES = {
    "upcoming", "mainboard", "sme", "big", "new", "check", "total",
    "record", "india", "crore", "cr", "million", "billion", "only",
    "from", "six", "nine", "four", "which", "the", "about", "where",
    "what", "why", "each", "click", "latest", "average", "korean",
    "rebounding", "rs", "sebi", "bse", "nse", "drhp", "gmp", "all",
    "top", "best", "key", "major", "five", "three", "two", "ten",
    "how", "when", "first", "last", "this", "that", "more", "most",
    "here", "there", "into", "over", "under", "after", "before",
    "amid", "versus", "vs", "per", "via", "and", "for", "with",
    "plans", "proposed", "christmas", "dual", "steel", "market",
    "revenue cagr post", "research centre", "industries", "healthcare",
    "historic", "download", "current", "global", "infra", "hour",
    "live", "open", "bold", "mixed", "these", "year", "ipos",
    "groundbreaking", "gleaming", "landmark", "firms eye",
    "stock brokers", "anchor investors back clean max",
    "fashion player kiaasa retail submits",
    "player pngs reva diamond jewellery",
    "in yaap digital ahead of",
    "ambani says targeting reliance jio",
    "reliance jio targets massive",
    "is shree ram twistex",
    "gaudium ivf announce",
    "pngs reva diamond jewellery files",
    "pngs reva diamond jewellery launches",
    "max & pngs reva diamond",
    "cleanmax enviro energy solutions limited",
    "does clean max enviro energy",
}

# ── Manual canonical names (always prefer these over fuzzy guesses) ───────────
MANUAL_NORMALIZE = {
    # CleanMax variants
    "Clean Max":                          "CleanMax Enviro Energy",
    "Clean Max Enviro":                   "CleanMax Enviro Energy",
    "Clean Max Enviro Energy":            "CleanMax Enviro Energy",
    "Clean Max Enviro Energy Solutions":  "CleanMax Enviro Energy",
    "CleanMax":                           "CleanMax Enviro Energy",
    "CleanMax Enviro":                    "CleanMax Enviro Energy",
    "Cleanmax":                           "CleanMax Enviro Energy",
    "Max Enviro Energy Solutions Ltd":    "CleanMax Enviro Energy",

    # YAAP Digital variants
    "YAAP Digital":                       "Yaap Digital",
    "YAAP DIGITAL LIMITED":               "Yaap Digital",

    # PNGS Reva variants
    "PNGS Reva":                          "PNGS Reva Diamond Jewellery",
    "PNGS Reva Diamond":                  "PNGS Reva Diamond Jewellery",
    "PNGS Reva Jewellery":               "PNGS Reva Diamond Jewellery",
    "Reva Diamond":                       "PNGS Reva Diamond Jewellery",
    "Reva Diamond Jewellery":            "PNGS Reva Diamond Jewellery",
    "Reva Diamonds":                      "PNGS Reva Diamond Jewellery",
    "Reva Diamonds Files":               "PNGS Reva Diamond Jewellery",
    "Reva Jewellery":                     "PNGS Reva Diamond Jewellery",

    # Omnitech
    "Omnitech":                           "Omnitech Engineering",

    # Gaudium IVF variants
    "Gaudium":                            "Gaudium IVF",
    "Gaudium IVF & Women Health":         "Gaudium IVF",

    # Striders Impex
    "Striders Impex Limited":             "Striders Impex",

    # Accord Transformer
    "Accord Transformer & Switchgear":    "Accord Transformer",

    # Fractal Analytics
    "Fractal AI":                         "Fractal Analytics",
    "Fractal Industries":                 "Fractal Analytics",

    # Shree Ram Twistex
    "Shree Ram":                          "Shree Ram Twistex",

    # PhonePe
    "PhonePe Files Draft":                "PhonePe",
    "Backed PhonePe":                     "PhonePe",

    # Mobilise App
    "Mobilise App":                       "Mobilise App Lab",
    "Mobilise App Lab Limited":           "Mobilise App Lab",

    # Women Health
    "Women Health":                       "Gaudium IVF",

    # ICICI Prudential AMC
    "ICICI Pru AMC":                      "ICICI Prudential AMC",

    # SBI
    "SBI Mutual Fund":                    "SBI Funds Management",

    # HDB Financial
    "HDB Financial":                      "HDB Financial Services",

    # Wakefit
    "Wakefit Innovations":                "Wakefit",

    # E Transportation
    "E Transportation":                   "E To E Transportation Infrastructure",

    # National Stock Exchange
    "National Stock Exchange":            "NSE",

    # Solarworld
    "Solarworld Energy Solutions":        "Solarworld Energy",

    # Studds
    "Studds":                             "Studds Accessories",

    # Bonfiglioli
    "Bonfiglioli Transmissions Limited":  "Bonfiglioli Transmissions",

    # Pride Hotels
    "Pride Hotels Limited":               "Pride Hotels",

    # Narmadesh
    "Narmadesh Brass":                    "Narmadesh Brass Industries",
}


def apply_manual_normalize(name: str) -> str:
    return MANUAL_NORMALIZE.get(name, name)


def is_junk(name: str) -> bool:
    if not name or not isinstance(name, str):
        return True
    name_stripped = name.strip()
    if len(name_stripped) < 5:
        return True
    if name_stripped.lower() in JUNK_NAMES:
        return True
    # Single word under 6 chars
    if len(name_stripped.split()) == 1 and len(name_stripped) < 6:
        return True
    return False


def fuzzy_deduplicate(names: list, threshold: int = 88) -> dict:
    """
    Auto-group similar names using fuzzy matching.
    Returns a dict mapping each name → canonical name.
    Canonical = the shortest clean version (usually the real company name).
    """
    canonical_map = {}
    # Sort by length so shorter names (cleaner) become canonical
    sorted_names = sorted(names, key=lambda x: len(x))
    assigned = {}  # name_lower → canonical

    for name in sorted_names:
        name_lower = name.lower()
        if name_lower in assigned:
            canonical_map[name] = assigned[name_lower]
            continue

        # Find similar names already assigned
        candidates = [n for n in assigned.keys()]
        if candidates:
            match = process.extractOne(
                name_lower,
                candidates,
                scorer=fuzz.token_sort_ratio
            )
            if match and match[1] >= threshold:
                # Map to whatever canonical that match was assigned to
                canonical_map[name] = assigned[match[0]]
                assigned[name_lower] = assigned[match[0]]
                continue

        # No match found — this name becomes its own canonical
        canonical_map[name] = name
        assigned[name_lower] = name

    return canonical_map


def signal(score: float) -> str:
    if score >= 0.05:
        return "BULLISH"
    elif score <= -0.05:
        return "BEARISH"
    else:
        return "NEUTRAL"


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df)} scored articles")

    # ── Step 1: Apply manual normalization ───────────────────────────────────
    df["ipo_name"] = df["ipo_name"].apply(apply_manual_normalize)

    # ── Step 2: Drop junk names ───────────────────────────────────────────────
    before = len(df)
    df = df[~df["ipo_name"].apply(is_junk)].copy()
    print(f"Dropped {before - len(df)} junk rows")

    # ── Step 3: Fuzzy deduplication ───────────────────────────────────────────
    unique_names = df["ipo_name"].dropna().unique().tolist()
    print(f"Unique names before fuzzy: {len(unique_names)}")

    fuzzy_map = fuzzy_deduplicate(unique_names, threshold=88)
    df["ipo_name"] = df["ipo_name"].map(fuzzy_map).fillna(df["ipo_name"])

    unique_after = df["ipo_name"].nunique()
    print(f"Unique names after fuzzy:  {unique_after}")

    # ── Step 4: Parse date ────────────────────────────────────────────────────
    date_col = None
    for col in ["published_date", "date", "published", "pubDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            date_col = col
            break

    # ── Step 5: Per-IPO summary ───────────────────────────────────────────────
    summary = df.groupby("ipo_name").agg(
        article_count       = ("sentiment_score", "count"),
        avg_sentiment_score = ("sentiment_score", "mean"),
        positive_count      = ("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count      = ("sentiment_label", lambda x: (x == "negative").sum()),
        neutral_count       = ("sentiment_label", lambda x: (x == "neutral").sum()),
        max_sentiment_score = ("sentiment_score", "max"),
        min_sentiment_score = ("sentiment_score", "min"),
    ).reset_index()

    summary["avg_sentiment_score"] = summary["avg_sentiment_score"].round(4)
    summary["positive_ratio"]      = (summary["positive_count"] / summary["article_count"]).round(4)
    summary["negative_ratio"]      = (summary["negative_count"] / summary["article_count"]).round(4)
    summary["signal"]              = summary["avg_sentiment_score"].apply(signal)

    summary.to_csv(SUMMARY_PATH, index=False)
    print(f"\n✅ Per-IPO summary saved → {SUMMARY_PATH}")
    print(summary[["ipo_name", "article_count", "avg_sentiment_score", "signal"]].to_string(index=False))

    # ── Step 6: Sentiment trend ───────────────────────────────────────────────
    if date_col:
        df["week"] = df[date_col].dt.to_period("W").astype(str)
        trend = df.groupby(["ipo_name", "week"]).agg(
            avg_sentiment = ("sentiment_score", "mean"),
            article_count = ("sentiment_score", "count"),
        ).reset_index()
        trend["avg_sentiment"] = trend["avg_sentiment"].round(4)
        trend.to_csv(TREND_PATH, index=False)
        print(f"✅ Sentiment trend saved → {TREND_PATH}")
    else:
        print("⚠️  No date column found — skipping trend output.")


if __name__ == "__main__":
    main()