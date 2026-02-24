"""
nlp/ipo_signal.py
Phase 5 — Final IPO Signal Generator
"""

import pandas as pd
import numpy as np
import os

SUMMARY_PATH = "data/processed/ipo_sentiment_summary.csv"
TREND_PATH   = "data/processed/ipo_sentiment_trend.csv"
OUT_PATH     = "data/processed/ipo_final_signals.csv"

os.makedirs("data/processed", exist_ok=True)

# ── Junk names to exclude from final output ───────────────────────────────────
JUNK_NAMES = {
    "plans", "proposed", "christmas", "dual", "steel", "market",
    "revenue cagr post", "research centre", "does clean max enviro energy",
    "can clean max", "cleanmax plans", "mrc infracon files",
    "phonepe files draft", "mobilise app", "mobilise app lab limited",
    "fractal industries", "shree ram", "pride hotels limited",
    "bonfiglioli transmissions limited", "clean max", "cleanmax enviro",
    "clean max enviro", "clean max enviro energy",
}

# ── Scoring weights ───────────────────────────────────────────────────────────
W_SENTIMENT   = 0.45
W_CONSISTENCY = 0.30
W_BUZZ        = 0.15
W_TREND       = 0.10


# ── Trend score ───────────────────────────────────────────────────────────────
def compute_trend_score(trend_df: pd.DataFrame, ipo_name: str) -> float:
    ipo_trend = trend_df[trend_df["ipo_name"] == ipo_name].copy()
    ipo_trend = ipo_trend[ipo_trend["week"] != "NaT"].dropna(subset=["week"])

    if len(ipo_trend) < 2:
        return 0.0

    ipo_trend = ipo_trend.sort_values("week")
    sentiments = ipo_trend["avg_sentiment"].values
    mid = len(sentiments) // 2
    trend = sentiments[mid:].mean() - sentiments[:mid].mean()
    return float(np.clip(trend, -1, 1))


# ── Normalize buzz with stronger separation ───────────────────────────────────
def normalize_buzz(article_counts: pd.Series) -> pd.Series:
    log_counts = np.log1p(article_counts)
    min_val = log_counts.min()
    max_val = log_counts.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(article_counts), index=article_counts.index)
    return (log_counts - min_val) / (max_val - min_val)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    summary = pd.read_csv(SUMMARY_PATH)
    trend   = pd.read_csv(TREND_PATH)
    print(f"  → {len(summary)} IPOs before filtering")

    # ── Remove junk names ─────────────────────────────────────────────────────
    summary = summary[
        ~summary["ipo_name"].str.lower().isin(JUNK_NAMES)
    ].copy()

    # Remove single-word names under 5 chars (fragments)
    summary = summary[
        summary["ipo_name"].apply(lambda x: len(str(x)) >= 5)
    ].copy()

    # Must have at least 2 words OR be a known short brand (4+ chars)
    summary = summary[
        summary["ipo_name"].apply(
            lambda x: len(str(x).split()) >= 2 or len(str(x)) >= 6
        )
    ].copy()

    print(f"  → {len(summary)} IPOs after filtering junk names")

    # ── Score: Sentiment (amplified) ──────────────────────────────────────────
    # Multiply by 3 before normalizing so small differences matter more
    amplified = (summary["avg_sentiment_score"] * 3).clip(-1, 1)
    summary["score_sentiment"] = ((amplified + 1) / 2).round(4)

    # ── Score: Consistency ────────────────────────────────────────────────────
    # Amplify the positive/negative gap
    consistency_raw = (summary["positive_ratio"] - summary["negative_ratio"]) * 2
    summary["score_consistency"] = ((consistency_raw.clip(-1, 1) + 1) / 2).round(4)

    # ── Score: Buzz ───────────────────────────────────────────────────────────
    summary["score_buzz"] = normalize_buzz(summary["article_count"]).round(4)

    # ── Score: Trend ──────────────────────────────────────────────────────────
    print("Computing trend scores...")
    raw_trends = summary["ipo_name"].apply(
        lambda name: compute_trend_score(trend, name)
    )
    summary["score_trend"] = ((raw_trends.clip(-1, 1) + 1) / 2).round(4)

    # ── Weighted final score ──────────────────────────────────────────────────
    summary["final_score"] = (
        W_SENTIMENT   * summary["score_sentiment"]   +
        W_CONSISTENCY * summary["score_consistency"] +
        W_BUZZ        * summary["score_buzz"]        +
        W_TREND       * summary["score_trend"]
    ).round(4)

    # ── Signal thresholds ─────────────────────────────────────────────────────
    summary["signal"] = summary["final_score"].apply(
        lambda s: "APPLY" if s >= 0.58 else ("AVOID" if s <= 0.42 else "NEUTRAL")
    )

    summary["confidence"] = summary["final_score"].apply(
        lambda s: "HIGH" if abs(s - 0.5) >= 0.15
                  else ("MEDIUM" if abs(s - 0.5) >= 0.08 else "LOW")
    )

    # ── Output ────────────────────────────────────────────────────────────────
    out_cols = [
        "ipo_name", "signal", "confidence", "final_score",
        "article_count", "avg_sentiment_score",
        "score_sentiment", "score_buzz", "score_consistency", "score_trend",
    ]
    output = summary[out_cols].sort_values("final_score", ascending=False)
    output.to_csv(OUT_PATH, index=False)

    # ── Print ─────────────────────────────────────────────────────────────────
    print(f"\n✅ Saved to {OUT_PATH}")
    print(f"\n{'='*68}")
    print(f"{'IPO NAME':<32} {'SIGNAL':<9} {'CONF':<8} {'SCORE':<8} {'ARTICLES'}")
    print(f"{'='*68}")

    for _, row in output.iterrows():
        print(
            f"{str(row['ipo_name']):<32} "
            f"{row['signal']:<9} "
            f"{row['confidence']:<8} "
            f"{row['final_score']:<8.4f} "
            f"{int(row['article_count'])}"
        )

    print(f"\n{'='*68}")
    print(f"APPLY:   {(output['signal'] == 'APPLY').sum()}")
    print(f"NEUTRAL: {(output['signal'] == 'NEUTRAL').sum()}")
    print(f"AVOID:   {(output['signal'] == 'AVOID').sum()}")
    print(f"{'='*68}")


if __name__ == "__main__":
    main()