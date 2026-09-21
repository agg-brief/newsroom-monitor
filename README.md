# Newsroom Monitor

A compact, TweetDeck-inspired newsroom monitoring dashboard built with Python and Streamlit. It combines public Telegram channels (via Telethon) and public RSS feeds—including RSS mirrors for X—into five filterable columns.

## Features

- Wide, responsive Streamlit dashboard with compact one-line posts.
- Entire post row links to the original source.
- Automatic browser refresh every 60 seconds.
- Search, category filtering, and source filtering.
- SQLite persistence with `external_id` uniqueness for deduplication.
- Recent posts first and a separate ingestion command.
- Type hints, environment-based configuration, and no official X API dependency.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env, then collect initial data
python collect.py
streamlit run app.py
```

The dashboard creates `data/newsroom.db` automatically. Run `python collect.py` periodically with cron, systemd, or a container scheduler. Streamlit refreshes the UI, while the collector updates the database; these are intentionally separate concerns.

## Configuration

`RSS_FEEDS_JSON` is a JSON object mapping one of the five category names to a list of public RSS URLs:

```env
RSS_FEEDS_JSON={"Israeli Government":["https://example.org/government.xml"],"Media & Journalists":["https://example.org/media.xml"]}
```

Telegram requires API credentials from <https://my.telegram.org>. Add public usernames (without or with `@`) to `TELEGRAM_CHANNELS`, comma separated. The first run may ask for an interactive login and creates a local Telethon session file; keep it private and do not commit it. The optional category mapping currently defaults Telegram channels to `Media & Journalists`; extend `collect.py` with a channel-to-category mapping when needed.

## Project layout

```text
app.py                  Streamlit UI and responsive styling
collect.py              RSS/Telegram ingestion CLI
collectors/             Typed source adapters and normalized Post model
database/               SQLite schema and repository
config/                 Environment-backed settings
data/                   Runtime SQLite database (ignored by git)
```

## Operations and safety

Use only channels and feeds you are authorized to access. This project uses RSS feeds only for X and does not call the official X API. Keep `.env`, Telegram session files, and the SQLite database out of version control. RSS publishers may throttle or change formats, so production deployments should add logging, retry/backoff, and health monitoring around `collect.py`.
