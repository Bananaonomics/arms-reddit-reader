# arms-reddit-reader

A small, read-only script for **personal, non-commercial research**: once an hour it reads the newest public post
titles in a few cryptocurrency subreddits and counts how often each coin is mentioned. It is the Reddit part of a
private personal research tool.

## What it does
- Uses Reddit's official Data API with application-only OAuth (no user login, no user data).
- Reads `/r/<subreddit>/new` for: r/CryptoCurrency, r/CryptoMarkets, r/SatoshiStreetBets, r/altcoin, r/Bitcoin,
  r/ethtrader, r/solana, r/memecoins. About 8 requests per hour.
- Counts posts whose titles mention each coin and appends the counts to a local CSV.

## What it never does
- No posting, commenting, voting, messaging, following or moderating.
- No collection of usernames or private data; no sharing, selling or republishing of Reddit data.
- No AI/model training on Reddit content.

## Use
1. Get Data API access from Reddit (Responsible Builder Policy) and create a "script" app.
2. Save its credentials to `reddit.json` next to the script (this file is git-ignored):
   `{"client_id": "...", "client_secret": "...", "user_agent": "arms-reddit-reader/1.0 by u/<account>"}`
3. Run `python3 reddit_reader.py` hourly (cron or Task Scheduler). Python 3.9+, standard library only.

## License
MIT
