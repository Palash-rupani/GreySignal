import pandas as pd
import re
import os

IN_PATH = "data/processed/all_news_ipo_only.csv"
OUT_PATH = "data/processed/ipo_tagged_news.csv"

PATTERNS = [
    r"ipo of ([a-zA-Z &]+)",
    r"([a-zA-Z &]+) ipo",
    r"([a-zA-Z &]+) files drhp",
    r"([a-zA-Z &]+) gets sebi nod",
    r"([a-zA-Z &]+) public issue",
    r"([a-zA-Z &]+) launches ipo",
    r"([a-zA-Z &]+) to raise",
]

df = pd.read_csv(IN_PATH)

print("Rows to tag:", len(df))

def extract_name(text):
    if not isinstance(text, str):
        return None

    for pat in PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    return None

df["ipo_name"] = df["text"].astype(str).apply(extract_name)

df.to_csv(OUT_PATH, index=False)

print("Tagged rows:", df["ipo_name"].notna().sum())
print("Saved to:", OUT_PATH)
