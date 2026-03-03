
# GreySignal

> A market intelligence dashboard that analyzes news sentiment and current coverage around companies ahead of their IPO — helping investors make informed decisions before a stock hits the market.

## Project Documentaion
https://docs.google.com/document/d/1j9-JBmBEhBGwKm3Ogbar5QUiq9mPM1r5_kYDdrKn7Uw/edit?usp=sharing

## Live Demo

🔗 **Frontend:** [grey-signal.vercel.app](https://grey-signal.vercel.app)  
⚙️ **Backend API:** [greysignal.onrender.com](https://greysignal.onrender.com)

> **Note:** Backend is hosted on Render's free tier and may take 30–60 seconds to wake up on first visit after a period of inactivity. The frontend will load instantly — just wait a moment for the data to appear.

---

## What it does

GreySignal scrapes and processes hundreds of financial news articles daily, runs them through a fine-tuned NLP model (FinBERT), and generates a **APPLY / NEUTRAL / AVOID** signal for each upcoming IPO based on:

- **Sentiment** — is the news coverage positive or negative?
- **Consistency** — is sentiment stable across multiple articles?
- **Buzz** — how much coverage is the IPO getting?
- **Trend** — is sentiment improving or declining over time?
- **GMP** — live grey market premium scraped daily

---

## Architecture

```
Google News RSS
      ↓
  Scraper (Python + feedparser)
      ↓
  Text Cleaning + IPO Filtering
      ↓
  FinBERT Sentiment Scoring
      ↓
  Signal Generator (weighted scoring formula)
      ↓
  GMP Scraper (ipowatch.in)
      ↓
  Neon PostgreSQL Database
      ↓
  FastAPI Backend (Render)
      ↓
  React Frontend (Vercel)
```

**Automated:** GitHub Actions runs the full pipeline daily at 9:00 AM IST — no manual intervention needed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| NLP Model | FinBERT (fine-tuned BERT for financial sentiment) |
| Pipeline | Python, pandas, feedparser, rapidfuzz |
| Backend | FastAPI, psycopg2 |
| Database | PostgreSQL (Neon) |
| Frontend | React, Recharts, React Router |
| Deployment | Vercel (frontend), Render (backend) |
| Automation | GitHub Actions (daily cron) |

---

## Signal Formula

```
Final Score = (Sentiment × 0.40) + (Consistency × 0.25) + (Buzz × 0.20) + (Trend × 0.15)

Score ≥ 0.60   →  APPLY
Score 0.40–0.60  →  NEUTRAL
Score ≤ 0.40   →  AVOID
```

---

## Features

- 📊 Dashboard with 150+ IPOs ranked by signal strength
- 🔴🟡🟢 APPLY / NEUTRAL / AVOID signals with confidence levels
- 📈 Live GMP (Grey Market Premium) data updated daily
- 🔍 Search, filter by signal/confidence, sort by score or GMP
- 📄 IPO detail page with score breakdown and sentiment gauge
- ⚡ Fully automated pipeline — fresh data every morning at 9 AM IST

---

## Running Locally

**Prerequisites:** Python 3.11+, Node.js 18+, a Neon PostgreSQL database

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Create .env file
echo "DATABASE_URL=your_neon_connection_string" > .env

uvicorn main:app --reload
# API available at http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install

# Create .env.local file
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
# App available at http://localhost:5173
```

**Pipeline (run manually):**
```bash
python scraping/google_news.py
python nlp/cleaning.py
python nlp/ipo_filter.py
python nlp/ipo_name_extractor.py
python nlp/sentiment.py
python nlp/aggregate_sentiment.py
python nlp/ipo_signal.py
python fundamentals/fetch_gmp.py
python tools/db_writer.py
```

---

## Project Structure

```
GreySignal/
├── scraping/          # News scrapers (Google News RSS, IPO discovery)
├── nlp/               # Text cleaning, sentiment scoring, signal generation
├── fundamentals/      # GMP scraper
├── tools/             # DB setup and writer scripts
├── backend/           # FastAPI app
├── frontend/          # React app
├── data/
│   ├── raw/           # Scraped data
│   └── processed/     # Cleaned and scored data
└── .github/workflows/ # GitHub Actions pipeline
```

---

## Roadmap

- [ ] Subscription data (NSE live subscription status)
- [ ] Price band + lot size
- [ ] Promoter holdings + OFS details
- [ ] Historical backtesting to validate signal accuracy
- [ ] Email/WhatsApp alerts for strong APPLY signals

---

## Author

**Palash Rupani**  
[github.com/Palash-rupani](https://github.com/Palash-rupani)