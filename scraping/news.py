import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

HEADERS = {"User-Agent": "Mozilla/5.0"}

BASE_URLS = {
    "livemint": "https://www.livemint.com/market/ipo",
    "moneycontrol": "https://www.moneycontrol.com/news/business/ipo/",
}

rows = []

for source, url in BASE_URLS.items():
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.select("a[href]"):
        link = a["href"]
        title = a.get_text(strip=True)

        if "ipo" not in link.lower():
            continue

        if link.startswith("/"):
            link = "https://www.moneycontrol.com" + link

        try:
            article = requests.get(link, headers=HEADERS, timeout=10)
            article_soup = BeautifulSoup(article.text, "html.parser")

            paragraphs = [p.get_text(" ", strip=True)
                          for p in article_soup.find_all("p")]

            rows.append({
                "source": source,
                "title": title,
                "url": link,
                "text": " ".join(paragraphs),
                "scraped_at": datetime.utcnow()
            })

        except Exception as e:
            print("Failed:", link)

df = pd.DataFrame(rows)

os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/news_articles.csv", index=False)

print(f"Saved {len(df)} articles.")
