"""arms-reddit-reader: read-only, hourly counts of which cryptocurrencies are mentioned in a few crypto subreddits.

Personal, non-commercial research. The app never posts, comments, votes, messages or moderates. Once an hour it
reads the newest public posts (titles only) from the subreddits below through Reddit's official Data API with
application-only OAuth, counts mentions of a list of coins, and appends the counts to a local CSV. Nothing is
shared, sold or republished. About 8 requests per hour.

Setup: put the approved app's credentials in reddit.json (never commit it):
    {"client_id": "...", "client_secret": "...", "user_agent": "arms-reddit-reader/1.0 by u/<your account>"}
Run:   python3 reddit_reader.py          (one pass; schedule it hourly)
Stdlib only (Python 3.9+).
"""
import base64
import csv
import datetime
import json
import os
import re
import time
import urllib.request

SUBREDDITS = ["CryptoCurrency", "CryptoMarkets", "SatoshiStreetBets", "altcoin", "Bitcoin", "ethtrader", "solana", "memecoins"]
COINS = {  # symbol: words that count as a mention (case-insensitive, whole words)
    "BTC": ["btc", "bitcoin"], "ETH": ["eth", "ethereum"], "SOL": ["sol", "solana"], "XRP": ["xrp", "ripple"],
    "DOGE": ["doge", "dogecoin"], "ADA": ["ada", "cardano"], "LINK": ["chainlink"], "AVAX": ["avax", "avalanche"],
    "PEPE": ["pepe"], "SHIB": ["shib", "shiba"], "BNB": ["bnb"], "TON": ["toncoin"], "HYPE": ["hyperliquid"],
}
CREDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reddit.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mentions.csv")
RX = {sym: re.compile(r"\b(" + "|".join(map(re.escape, words)) + r")\b", re.I) for sym, words in COINS.items()}


def token(creds):
    auth = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    req = urllib.request.Request("https://www.reddit.com/api/v1/access_token", data=b"grant_type=client_credentials",
                                 headers={"Authorization": "Basic " + auth, "User-Agent": creds["user_agent"]})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["access_token"]


def newest_titles(tok, ua, sub):
    req = urllib.request.Request(f"https://oauth.reddit.com/r/{sub}/new?limit=100", headers={"Authorization": "Bearer " + tok, "User-Agent": ua})
    return [c["data"].get("title", "") for c in json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]["children"]]


def main():
    creds = json.load(open(CREDS, encoding="utf-8"))
    tok = token(creds)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")
    rows = []
    for sub in SUBREDDITS:
        titles = newest_titles(tok, creds["user_agent"], sub)
        for sym, rx in RX.items():
            n = sum(1 for t in titles if rx.search(t))
            if n:
                rows.append({"at": now, "subreddit": sub, "coin": sym, "posts_mentioning": n, "posts_read": len(titles)})
        time.sleep(1.5)  # gentle pacing, far under the rate limit
    new = not os.path.exists(OUT)
    with open(OUT, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["at", "subreddit", "coin", "posts_mentioning", "posts_read"], lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"{now}: {len(rows)} coin/subreddit counts written")


if __name__ == "__main__":
    main()
