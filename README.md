# GreySignal

GreySignal is an NLP-driven research system designed to analyze sentiment, fundamentals,
and grey-market signals of Indian IPOs before listing to help assess whether retail
investors should apply.

---

## Project Documentaion
-https://docs.google.com/document/d/1EOJDnqaCvTLfFMGPiRTyavlOOKWewe9dmcUq23U-_5Y/edit?usp=sharing

---
## 📌 What GreySignal Does

- Scrapes social platforms (Reddit, X, forums) and financial news for IPO discussions
- Quantifies bullish vs bearish sentiment using NLP models
- Extracts fundamentals from DRHP / RHP prospectus documents
- Tracks grey market premium (GMP) and subscription-related signals
- Combines all signals into an Apply / Neutral / Avoid recommendation
- Provides explanations for each recommendation

---

## 🎯 Project Goal

Predict the attractiveness of applying to an IPO *before listing* by estimating
likely listing-day performance using:

- Social sentiment
- News tone
- Financial fundamentals
- Grey-market trends
- Sector conditions
- Historical IPO outcomes

---

## 🧠 Tech Stack

- Python, Pandas, NumPy
- PyTorch & HuggingFace Transformers
- Web scraping (PRAW, BeautifulSoup, Selenium)
- PDF parsing & OCR (pdfplumber, pytesseract)
- Scikit-learn, XGBoost
- Streamlit dashboard
- FastAPI backend
- SHAP for model explainability
- PostgreSQL / SQLite for storage

---

## 📂 Repository Structure

greysignal-ipo/
│
├── data/
│ ├── raw/
│ ├── processed/
│ └── labels/
│
├── scraping/
├── nlp/
├── fundamentals/
├── features/
├── models/
├── dashboard/
├── notebooks/
├── docs/
│
├── requirements.txt
└── README.md


---

## ⚠️ Disclaimer

GreySignal is for educational and research purposes only.
This project does **not** provide financial or investment advice.
Use at your own risk.

---

## 🗺️ Roadmap

- [ ] Historical Indian IPO dataset creation  
- [ ] Social & news scraping pipelines  
- [ ] Sentiment analysis models  
- [ ] DRHP / RHP NLP extraction  
- [ ] GMP & subscription tracking  
- [ ] Feature engineering  
- [ ] Prediction model training  
- [ ] Explainability layer  
- [ ] Streamlit dashboard  

Detailed plans are in the `/docs` folder.

---

## 🤝 Contributing

This is currently a personal research project.
Contributions and suggestions are welcome once the core MVP is ready.

---

## 📬 Contact

Created as a data-science & NLP project for Indian capital markets research.