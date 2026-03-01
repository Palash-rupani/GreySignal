from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import psycopg2.extras
import math
import os

app = FastAPI(title="GreySignal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # temporarily allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

CONN_STR = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_3uLskzKn6BSp@ep-dawn-tooth-aif90raf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)


def get_conn():
    return psycopg2.connect(CONN_STR, cursor_factory=psycopg2.extras.RealDictCursor)


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def clean_row(row):
    return {k: clean(v) for k, v in dict(row).items()}


@app.get("/")
def root():
    return {"status": "ok", "service": "GreySignal API"}


@app.get("/api/signals")
def get_signals():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT ipo_name, signal, confidence, final_score, article_count,
               avg_sentiment, score_sentiment, score_buzz, score_consistency,
               score_trend, gmp, gmp_percent,
               subscription_rate, price_band_low, price_band_high,
               lot_size, open_date, close_date, listing_date,
               promoter_holding, ofs_percent, updated_at
        FROM ipo_signals
        ORDER BY final_score DESC NULLS LAST
    """)
    rows = [clean_row(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return JSONResponse(content=rows)


@app.get("/api/stats")
def get_stats():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*)                                    AS total,
            COUNT(*) FILTER (WHERE signal = 'APPLY')   AS apply,
            COUNT(*) FILTER (WHERE signal = 'NEUTRAL') AS neutral,
            COUNT(*) FILTER (WHERE signal = 'AVOID')   AS avoid,
            COALESCE(SUM(article_count), 0)            AS articles,
            COUNT(*) FILTER (WHERE gmp IS NOT NULL)    AS gmp_tracked
        FROM ipo_signals
    """)
    row = clean_row(cur.fetchone())
    cur.close()
    conn.close()
    return JSONResponse(content=row)


@app.get("/api/ipo/{name}")
def get_ipo(name: str):
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT * FROM ipo_signals WHERE LOWER(ipo_name) = LOWER(%s)", (name,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return JSONResponse(content={"error": "IPO not found"})

    data = clean_row(row)

    # Attach trend
    cur.execute("""
        SELECT week, avg_sentiment, article_count
        FROM ipo_trend
        WHERE LOWER(ipo_name) = LOWER(%s)
        ORDER BY week
    """, (name,))
    data["trend"] = [clean_row(r) for r in cur.fetchall()]

    cur.close()
    conn.close()
    return JSONResponse(content=data)


@app.get("/api/ipo/{name}/trend")
def get_trend(name: str):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT week, avg_sentiment, article_count
        FROM ipo_trend
        WHERE LOWER(ipo_name) = LOWER(%s)
        ORDER BY week
    """, (name,))
    rows = [clean_row(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return JSONResponse(content=rows)