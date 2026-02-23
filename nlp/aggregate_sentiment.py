import pandas as pd

INPUT_PATH   = "data/processed/ipo_sentiment_scored.csv"
SUMMARY_PATH = "data/processed/ipo_sentiment_summary.csv"
TREND_PATH   = "data/processed/ipo_sentiment_trend.csv"

def main():
    df = pd.read_csv(INPUT_PATH)

    # ── Ensure date column is parsed ─────────────────────────────────────
    date_col = None
    for col in ["published_date", "date", "published", "pubDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            date_col = col
            break

    # ── Per-IPO Summary ──────────────────────────────────────────────────
    summary = df.groupby("ipo_name").agg(
        article_count         = ("sentiment_score", "count"),
        avg_sentiment_score   = ("sentiment_score", "mean"),
        positive_count        = ("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count        = ("sentiment_label", lambda x: (x == "negative").sum()),
        neutral_count         = ("sentiment_label", lambda x: (x == "neutral").sum()),
        max_sentiment_score   = ("sentiment_score", "max"),
        min_sentiment_score   = ("sentiment_score", "min"),
    ).reset_index()

    summary["avg_sentiment_score"] = summary["avg_sentiment_score"].round(4)
    summary["positive_ratio"]      = (summary["positive_count"] / summary["article_count"]).round(4)
    summary["negative_ratio"]      = (summary["negative_count"] / summary["article_count"]).round(4)

    # Signal label based on avg score
# Signal label based on avg score
    def signal(score):
        if score >= 0.05:    return "BULLISH"
        elif score <= -0.05: return "BEARISH"
        else:                return "NEUTRAL"

    summary["signal"] = summary["avg_sentiment_score"].apply(signal)

    summary.to_csv(SUMMARY_PATH, index=False)
    print(f"✅ Per-IPO summary saved → {SUMMARY_PATH}")
    print(summary[["ipo_name", "article_count", "avg_sentiment_score", "signal"]].to_string(index=False))

    # ── Sentiment Trend Over Time ─────────────────────────────────────────
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