# db_setup.py — Run once to create tables and migrate existing CSV data to Neon
# Usage: python tools/db_setup.py

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import math

CONN_STR = "postgresql://neondb_owner:npg_3uLskzKn6BSp@ep-dawn-tooth-aif90raf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNALS_CSV = os.path.join(BASE_DIR, "data", "processed", "ipo_final_signals.csv")
GMP_CSV     = os.path.join(BASE_DIR, "data", "raw", "gmp_data.csv")

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS ipo_signals (
    ipo_name          TEXT PRIMARY KEY,
    signal            TEXT,
    confidence        TEXT,
    final_score       FLOAT,
    article_count     INT,
    avg_sentiment     FLOAT,
    score_sentiment   FLOAT,
    score_buzz        FLOAT,
    score_consistency FLOAT,
    score_trend       FLOAT,
    gmp               FLOAT,
    gmp_percent       FLOAT,
    subscription_rate FLOAT,
    price_band_low    INT,
    price_band_high   INT,
    lot_size          INT,
    open_date         DATE,
    close_date        DATE,
    listing_date      DATE,
    promoter_holding  FLOAT,
    ofs_percent       FLOAT,
    updated_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ipo_trend (
    id            SERIAL PRIMARY KEY,
    ipo_name      TEXT,
    week          TEXT,
    avg_sentiment FLOAT,
    article_count INT,
    updated_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ipo_signals_signal ON ipo_signals(signal);
CREATE INDEX IF NOT EXISTS idx_ipo_trend_name ON ipo_trend(ipo_name);
"""


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def load_gmp():
    if not os.path.exists(GMP_CSV):
        return {}
    df = pd.read_csv(GMP_CSV)
    df["ipo_name"] = df["ipo_name"].astype(str).str.strip()
    return {row["ipo_name"]: row for _, row in df.iterrows()}


def main():
    print("Connecting to Neon...")
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()

    print("Creating tables...")
    cur.execute(CREATE_TABLE)
    conn.commit()
    print("✅ Tables created")

    # Load signals CSV
    print("\nLoading signals CSV...")
    df = pd.read_csv(SIGNALS_CSV)
    print(f"  {len(df)} rows loaded")

    # Load GMP
    gmp_data = load_gmp()
    print(f"  {len(gmp_data)} GMP entries loaded")

    # Fuzzy match GMP
    try:
        from rapidfuzz import process, fuzz

        gmp_names = list(gmp_data.keys())

        def get_gmp(name):
            if not gmp_names:
                return None, None
            match = process.extractOne(
                str(name),
                gmp_names,
                scorer=fuzz.token_sort_ratio
            )
            if match and match[1] >= 80:
                row = gmp_data[match[0]]
                return clean(row.get("gmp")), clean(row.get("gmp_percent"))
            return None, None

    except ImportError:

        def get_gmp(name):
            return None, None

    # Build rows
    print("\nInserting into Neon DB...")
    rows = []

    for _, r in df.iterrows():
        gmp, gmp_pct = get_gmp(r["ipo_name"])

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

    execute_values(
        cur,
        """
        INSERT INTO ipo_signals (
            ipo_name, signal, confidence, final_score, article_count,
            avg_sentiment, score_sentiment, score_buzz, score_consistency,
            score_trend, gmp, gmp_percent
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
        """,
        rows
    )

    conn.commit()
    print(f"✅ {len(rows)} IPOs inserted/updated")

    # Load trend CSV
    trend_path = os.path.join(
        BASE_DIR, "data", "processed", "ipo_sentiment_trend.csv"
    )

    if os.path.exists(trend_path):
        print("\nLoading trend data...")
        tdf = pd.read_csv(trend_path)

        cur.execute("DELETE FROM ipo_trend")

        trend_rows = [
            (
                str(r["ipo_name"]),
                str(r["week"]),
                clean(r.get("avg_sentiment")),
                int(r.get("article_count", 0)),
            )
            for _, r in tdf.iterrows()
        ]

        execute_values(
            cur,
            """
            INSERT INTO ipo_trend (ipo_name, week, avg_sentiment, article_count)
            VALUES %s
            """,
            trend_rows,
        )

        conn.commit()
        print(f"✅ {len(trend_rows)} trend rows inserted")

    # Verify
    cur.execute("SELECT COUNT(*) FROM ipo_signals")
    count = cur.fetchone()[0]

    cur.execute(
        """
        SELECT ipo_name, signal, final_score, gmp
        FROM ipo_signals
        ORDER BY final_score DESC
        LIMIT 5
        """
    )
    top = cur.fetchall()

    print(f"\n✅ Database has {count} IPOs")
    print("\nTop 5 IPOs:")
    for row in top:
        print(f"  {row[0]:<35} {row[1]:<8} {row[2]:.3f}  GMP: {row[3]}")

    cur.close()
    conn.close()

    print("\n✅ Migration complete!")


if __name__ == "__main__":
    main()