import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime
import os

QUERY = "IPO India apply OR DRHP OR listing OR grey market IPO"
LIMIT = 500

rows = []

for tweet in sntwitter.TwitterSearchScraper(QUERY).get_items():
    if len(rows) >= LIMIT:
        break

    rows.append({
        "source": "twitter",
        "date": tweet.date,
        "username": tweet.user.username,
        "content": tweet.content,
        "likeCount": tweet.likeCount,
        "retweetCount": tweet.retweetCount,
        "replyCount": tweet.replyCount,
        "url": tweet.url,
    })

df = pd.DataFrame(rows)

os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/twitter_ipo_posts.csv", index=False)

print(f"Saved {len(df)} tweets.")
