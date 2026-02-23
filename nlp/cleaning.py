import pandas as pd
import re
import os
import glob
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords", quiet=True)

STOPWORDS = set(stopwords.words("english"))

RAW_DIR  = "data/raw"
OUT_PATH = "data/processed/all_news_clean.csv"

os.makedirs("data/processed", exist_ok=True)

files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
print("Raw files found:", files)

dfs = []

for f in files:
    try:
        if os.path.getsize(f) == 0:
            print("Skipping empty file:", f)
            continue

        df = pd.read_csv(f)

        if df.empty:
            print("Skipping no-row file:", f)
            continue

        df["raw_file"] = os.path.basename(f)

        # Force all columns to string-safe types
        df = df.astype(object).where(df.notna(), other="")

        # ── Pick the best text column available ──────────────────────────
        # Priority: full_text > summary > text > title
        if "full_text" in df.columns and df["full_text"].astype(str).str.len().mean() > 100:
            df["text"] = df["full_text"]
            print(f"  {os.path.basename(f)}: using full_text column")
        elif "summary" in df.columns:
            df["text"] = df["summary"]
            print(f"  {os.path.basename(f)}: using summary column")
        elif "text" not in df.columns and "title" in df.columns:
            df["text"] = df["title"]
            print(f"  {os.path.basename(f)}: using title column")
        else:
            print(f"  {os.path.basename(f)}: using text column")

        dfs.append(df)

    except Exception as e:
        print("Skipping unreadable file:", f, "->", e)

if not dfs:
    print("No files loaded. Exiting.")
    exit()

all_df = pd.concat(dfs, ignore_index=True)
print("Total raw rows loaded:", len(all_df))

# ── Deduplication ─────────────────────────────────────────────────────────────
before = len(all_df)
all_df = all_df.drop_duplicates(subset=["text"], keep="first")
print(f"Dropped {before - len(all_df)} duplicate rows")


def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [t for t in text.split() if t not in STOPWORDS]

    return " ".join(tokens)


all_df["clean_text"] = all_df["text"].astype(str).apply(clean_text)

all_df = all_df[all_df["clean_text"].str.len() > 20]

all_df.to_csv(OUT_PATH, index=False)

print("Saved to:", OUT_PATH)
print("Rows after cleaning:", len(all_df))