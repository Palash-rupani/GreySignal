# GreySignal Architecture

GreySignal is a modular NLP and data-science system that evaluates Indian IPOs
before listing to determine whether retail investors should apply.

---

## High-Level Pipeline

Sources → Scrapers → Cleaning → NLP → Fundamentals → Features → Model → Dashboard

---

## Data Sources

- Financial news websites (LiveMint, Moneycontrol, Business Standard)
- Social platforms (Reddit – pending API approval)
- IPO portals and GMP blogs
- SEBI / NSE filings (DRHP / RHP PDFs)

---

## System Components

### 1. Scraping Layer (`/scraping`)
Collects raw text, URLs, timestamps, and source metadata.

Outputs saved to `data/raw/`.

---

### 2. Cleaning & NLP Layer (`/nlp`)
- Removes boilerplate HTML
- Normalizes text
- Detects company names
- Language detection
- Deduplication

Outputs saved to `data/processed/`.

---

### 3. Sentiment Engine
Uses finance-specific language models (FinBERT) and rule-based heuristics
to compute bullish/bearish scores and discussion volume.

---

### 4. Fundamentals Parser (`/fundamentals`)
Parses DRHP / RHP PDFs to extract:
- Revenue growth
- Profitability
- Debt ratios
- Promoter shareholding
- Risk disclosures

---

### 5. Feature Engineering (`/features`)
Merges sentiment, fundamentals, GMP signals, and market conditions
into a unified IPO-level dataset.

---

### 6. Prediction Model (`/models`)
Trains ML models to predict listing-day performance and assign
Apply / Neutral / Avoid recommendations.

---

### 7. Dashboard (`/dashboard`)
Visualizes IPO profiles, sentiment timelines, and recommendations
using Streamlit.

---

## Data Storage

- Raw data: `data/raw/`
- Cleaned data: `data/processed/`
- Labels: `data/labels/`
- SQLite / PostgreSQL for structured storage

---

## Ethics & Limitations

GreySignal is for research purposes only and not financial advice.
Scraping respects robots.txt and public content.
