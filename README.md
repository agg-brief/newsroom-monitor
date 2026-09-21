# Newsroom Monitor

A free, local-first newsroom monitoring dashboard inspired by TweetDeck. It is optimized for AFP-style scanning across Israel, the Palestinian territories, Lebanon and regional developments.

## Constraints and architecture

- Streamlit frontend, dark five-column newsroom layout.
- SQLite only; no cloud database, AWS, paid service or OpenAI API.
- RSS only for X content—there is no official X API integration.
- Telethon for public Telegram channels.
- Configuration lives in `config/sources.yaml`; credentials live in environment variables.
- The UI refreshes every 60 seconds, while collection runs independently through `collect.py`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit config/sources.yaml with confirmed RSS URLs and public Telegram usernames
python collect.py
streamlit run app.py
```

Schedule `python collect.py` with cron, systemd, or a local scheduler. Streamlit Community Cloud can run the UI for free, but its local filesystem is ephemeral; for persistent newsroom history, run the collector and dashboard on a machine with persistent storage. Never commit `.env` or a Telethon session.

## Sources

All requested initial sources and additional regional categories are present in `config/sources.yaml`. RSS entries intentionally use `example.invalid` placeholders until the correct public RSS endpoint is confirmed. Replace them with actual RSS URLs; unresolved placeholders are ignored by the collector. Telegram channel values likewise need confirmation and should be public usernames.

Each source has a category, platform, display name, URL/channel and optional language. Add sources without changing application code.

## Dashboard

The five primary columns scroll independently and show compact `HH:MM | Source | Headline` rows. Rows are fully clickable and open the original URL in a new tab. Search, category and source filters are in the sidebar. Headlines containing `hostage`, `ceasefire`, `cabinet`, `iran`, `hezbollah`, `rocket`, `airstrike`, `settlement`, `evacuation` or `aid` receive a red priority treatment.

## Database and deduplication

`database/schema.sql` defines the requested `posts` fields and indexes. `utils/hashing.py` creates a normalized SHA-256 `content_hash`; SQLite's unique constraint and `INSERT OR IGNORE` prevent duplicate rows across repeated collection runs and feeds.

## Telegram authentication

Create free Telegram API credentials at <https://my.telegram.org>, place them in `.env`, and run `python collect.py` interactively once. Telethon may request a phone number, login code and optional 2FA password. The session is saved under `TELEGRAM_SESSION` and must remain private.

## Free deployment notes

Streamlit Community Cloud is suitable for the UI using this repository and `app.py` as the entry point. Add the non-secret settings in the app configuration and secrets for Telegram credentials. Because Community Cloud does not provide a durable background scheduler or durable SQLite volume, run collection locally or on another free machine and understand that the dashboard's local database can reset on redeploy.
