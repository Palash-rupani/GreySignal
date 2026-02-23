import pandas as pd
import re

IN_PATH  = "data/processed/all_news_ipo_only.csv"
OUT_PATH = "data/processed/ipo_tagged_news.csv"

# ── Known company name stopwords ─────────────────────────────────────────────
# Words that should NEVER appear in a valid company name
NAME_STOPWORDS = {
    "upcoming", "mainboard", "sme", "big", "new", "check", "total", "record",
    "india", "crore", "cr", "million", "billion", "only", "from", "six",
    "nine", "four", "which", "the", "about", "where", "what", "why", "each",
    "click", "latest", "average", "korean", "rebounding", "rs", "ipo",
    "sebi", "bse", "nse", "drhp", "gmp", "all", "top", "best", "key",
    "major", "five", "three", "two", "ten", "how", "when", "first", "last",
    "this", "that", "more", "most", "many", "some", "other", "your", "our",
    "their", "its", "has", "have", "had", "was", "were", "will", "would",
    "here", "there", "into", "over", "under", "after", "before", "during",
    "amid", "versus", "vs", "per", "via", "and", "for", "with",

    # ── Step 1: added stopwords ──
    "unprecedented", "indian", "startup", "biggest", "resorts",
    "spacex", "backed", "largest", "booming", "busiest"
}

# ── Step 2: Name normalization map ───────────────────────────────────────────
NORMALIZE = {
    "Shadowfax Tech": "Shadowfax Technologies",
    "Shadowfax": "Shadowfax Technologies",
    "Advit Jewels Limited": "Advit Jewels",
    "Meesho Files": "Meesho",
    "Hannah Joseph": "Hannah Joseph Hospital",
    "PhonePe PhonePe": "PhonePe",
    "Backed PhonePe": "PhonePe",
    "UPL Subsidiary Advanta Enterprises": "Advanta Enterprises",
    "E Transportation Infrastructure": "E Transportation",
    "Madhur Iron & Steel Files": "Madhur Iron & Steel",
    "Fujiyama Power Systems": "Fujiyama Power",
    "Kanishk Aluminium India": "Kanishk Aluminium",
    "SMEs TO Launch": None,
    "Indian Stock Exchanges Following Successful": None,
    "Fractal Analytics & Others": "Fractal Analytics",
    "Clean Max Enviro Energy Solutions": "CleanMax Enviro Energy",
    "Clean Max Enviro Energy":           "CleanMax Enviro Energy",
    "Clean Max Enviro":                  "CleanMax Enviro Energy",
    "Clean Max":                         "CleanMax Enviro Energy",
    "CleanMax Enviro":                   "CleanMax Enviro Energy",
    "CleanMax Plans":                    "CleanMax Enviro Energy",
    "Can Clean Max":                     "CleanMax Enviro Energy",
    "Does Clean Max Enviro Energy":      None,
    "Mobilise App Lab Limited":          "Mobilise App Lab",
    "Mobilise App":                      "Mobilise App Lab",
    "Bonfiglioli Transmissions Limited": "Bonfiglioli Transmissions",
    "Pride Hotels Limited":              "Pride Hotels",
    "PhonePe Files Draft":               "PhonePe",
    "Fractal Industries":                "Fractal Analytics",
    "Shree Ram":                         "Shree Ram Twistex",
    "Plans":    None,
    "Proposed": None,
    "Christmas": None,
    "Dual":     None,
    "Steel":    None,
    "Market":   None,
    "Revenue CAGR Post": None,
    "Research Centre":   None,
}

# ── Regex patterns (1–5 word company name, title-cased) ──────────────────────
# Each pattern captures a NAMED GROUP called "name"
_COMPANY = r"(?P<name>[A-Z][a-zA-Z&]*(?:\s[A-Z&][a-zA-Z&]*){0,4})"

PATTERNS = [
    rf"IPO of {_COMPANY}",
    rf"{_COMPANY} IPO",
    rf"{_COMPANY} [Ff]iles [Dd]RHP",
    rf"{_COMPANY} [Gg]ets [Ss]ebi [Nn]od",
    rf"{_COMPANY} [Gg]ets SEBI [Nn]od",
    rf"{_COMPANY} [Ss]ecures SEBI",
    rf"{_COMPANY} [Rr]eceives SEBI",
    rf"{_COMPANY} [Pp]ublic [Ii]ssue",
    rf"{_COMPANY} [Ll]aunches IPO",
    rf"{_COMPANY} [Tt]o [Rr]aise",
    rf"{_COMPANY} [Ll]ists [Oo]n",
    rf"{_COMPANY} [Pp]repares for IPO",
]


def extract_name(text: str):
    if not isinstance(text, str):
        return None

    for pat in PATTERNS:
        m = re.search(pat, text)
        if m:
            candidate = m.group("name").strip()
            if is_valid_ipo_name(candidate):
                return candidate
    return None


def is_valid_ipo_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False

    name = name.strip()

    # Length guards
    if len(name) < 3 or len(name) > 50:
        return False

    # Must start with uppercase
    if not name[0].isupper():
        return False

    words = name.split()

    # Single-word names must be 4+ chars (avoids "Cr", "Rs", "An")
    if len(words) == 1 and len(name) < 4:
        return False

    # Reject if ANY word is a stopword
    if any(w.lower() in NAME_STOPWORDS for w in words):
        return False

    # Must have at least one real alphabetic word
    real_words = [w for w in words if re.match(r"[A-Za-z]{2,}", w)]
    if not real_words:
        return False

    return True


# ── Pipeline ──────────────────────────────────────────────────────────────────
print("Reading:", IN_PATH)
df = pd.read_csv(IN_PATH)
print("Rows to tag:", len(df))

text_col = "title" if "title" in df.columns else "text"
print(f"Extracting from column: '{text_col}'")

df["ipo_name"] = df[text_col].apply(extract_name)

before = df["ipo_name"].notna().sum()
print(f"Extracted (before cleaning): {before}")

df = df[df["ipo_name"].notna()].copy()

# ── Step 3: Apply normalization ──────────────────────────────────────────────
df["ipo_name"] = df["ipo_name"].apply(lambda x: NORMALIZE.get(x, x))
df = df[df["ipo_name"].notna()]

print(f"Tagged rows (after normalization): {len(df)}")

df.to_csv(OUT_PATH, index=False)
print("Saved to:", OUT_PATH)