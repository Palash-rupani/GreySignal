import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

url = "https://www.chittorgarh.com/ipo/bharat-coking-coal-ipo/1/"
print(f"Fetching: {url}\n")

r = requests.get(url, headers=HEADERS, timeout=10)
print(f"Status code: {r.status_code}\n")

soup = BeautifulSoup(r.text, "html.parser")

# Print ALL tables and their content
tables = soup.find_all("table")
print(f"Found {len(tables)} tables on page\n")

for i, table in enumerate(tables):
    print(f"=== TABLE {i} ===")
    for row in table.find_all("tr"):
        cols = row.find_all(["td", "th"])
        texts = [c.get_text(strip=True) for c in cols]
        if texts:
            print(texts)
    print()

# Also check for common div-based layouts (some sites don't use tables)
print("\n=== DIVS with 'price' or 'band' in text ===")
for div in soup.find_all(["div", "span", "p"]):
    text = div.get_text(strip=True).lower()
    if any(kw in text for kw in ["price band", "issue size", "open date", "close date", "listing"]):
        print(repr(div.get_text(strip=True)[:200]))