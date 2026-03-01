"""
db_writer.py — Called at end of pipeline to push results to Neon DB
Usage: python tools/db_writer.py
Add this as the last step in your run_pipeline.bat
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import math

CONN_STR = os.environ.get(
    "DATABASE_URL",
)

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNALS_CSV = os.path.join(BASE_DIR, "data", "processed", "ipo_final_signals.csv")
GMP_CSV     = os.path.join(BASE_DIR, "data", "raw", "gmp_data.csv")
TREND_CSV   = os.path.join(BASE_DIR, "data", "processed", "ipo_sentiment_trend.csv")


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def get_gmp_map():
    if not os.path.exists(GMP_CSV):
        return {}
    try:
        from rapidfuzz import process, fuzz
        df = pd.read_csv(GMP_CSV)
        df["ipo_name"] = df["ipo_name"].str.strip()
        gmp_names = df["ipo_name"].tolist()

        def lookup(name):
            match = process.extractOne(name, gmp_names, scorer=fuzz.token_sort_ratio)
            if match and match[1] >= 80:
                row = df[df["ipo_name"] == match[0]].iloc[0]
                return clean(row.get("gmp")), clean(row.get("gmp_percent"))
            return None, None
        return lookup
    except Exception:
        return lambda name: (None, None)


def main():
    print("=" * 50)
    print("DB Writer — pushing pipeline results to Neon")
    print("=" * 50)

    df = pd.read_csv(SIGNALS_CSV)
    print(f"Loaded {len(df)} signals")

    gmp_lookup = get_gmp_map()

    conn = psycopg2.connect(CONN_STR)
    cur  = conn.cursor()

    # Upsert signals
    rows = []
    for _, r in df.iterrows():
        gmp, gmp_pct = gmp_lookup(r["ipo_name"]) if callable(gmp_lookup) else (None, None)
        rows.append((
            str(r["ipo_name"]),
            str(r.get("signal", "NEUTRAL")),
            str(r.get("confidence", "LOW")),
            clean(r.get("final_score")),
            int(r.get("article_count", 0)),
            clean(r.get("avg_sentiment_score")),
            clean(r.get("score_sentiment")),
            clean(r.get("score_buzz")),
            clean(r.get("score_consistency")),
            clean(r.get("score_trend")),
            gmp,
            gmp_pct,
        ))

    execute_values(cur, """
        INSERT INTO ipo_signals (
            ipo_name, signal, confidence, final_score, article_count,
            avg_sentiment, score_sentiment, score_buzz, score_consistency,
            score_trend, gmp, gmp_percent, updated_at
        ) VALUES %s
        ON CONFLICT (ipo_name) DO UPDATE SET
            signal            = EXCLUDED.signal,
            confidence        = EXCLUDED.confidence,
            final_score       = EXCLUDED.final_score,
            article_count     = EXCLUDED.article_count,
            avg_sentiment     = EXCLUDED.avg_sentiment,
            score_sentiment   = EXCLUDED.score_sentiment,
            score_buzz        = EXCLUDED.score_buzz,
            score_consistency = EXCLUDED.score_consistency,
            score_trend       = EXCLUDED.score_trend,
            gmp               = EXCLUDED.gmp,
            gmp_percent       = EXCLUDED.gmp_percent,
            updated_at        = NOW()
    """, rows)
    conn.commit()
    print(f"✅ {len(rows)} IPOs upserted to DB")

    # Upsert trend
    if os.path.exists(TREND_CSV):
        tdf = pd.read_csv(TREND_CSV)
        cur.execute("DELETE FROM ipo_trend")
        trend_rows = [
            (str(r["ipo_name"]), str(r["week"]), clean(r.get("avg_sentiment")), int(r.get("article_count", 0)))
            for _, r in tdf.iterrows()
        ]
        execute_values(cur, """
            INSERT INTO ipo_trend (ipo_name, week, avg_sentiment, article_count)
            VALUES %s
        """, trend_rows)
        conn.commit()
        print(f"✅ {len(trend_rows)} trend rows updated")

    cur.close()
    conn.close()
    print("✅ Done!")


if __name__ == "__main__":
    main()