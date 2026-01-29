import pandas as pd
import os

IN_PATH = "data/processed/all_news_clean.csv"
OUT_PATH = "data/processed/all_news_ipo_only.csv"

KEYWORDS = [
    "ipo",
    "public issue",
    "listing",
    "drhp",
    "rhp",
    "sebi",
    "subscription",
    "anchor investor",
    "grey market",
    "gmp",
]

df = pd.read_csv(IN_PATH)

print("Input rows:", len(df))

def is_ipo_related(text):
    text = str(text).lower()
    return any(k in text for k in KEYWORDS)

df = df[df["clean_text"].apply(is_ipo_related)]

os.makedirs("data/processed", exist_ok=True)
df.to_csv(OUT_PATH, index=False)

print("IPO-related rows:", len(df))
print("Saved to:", OUT_PATH)
