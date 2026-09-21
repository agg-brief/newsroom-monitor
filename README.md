# Newsroom Monitor

This deployment monitors only the requested X accounts through public RSS mirrors and configured public Telegram channels. It does not ingest general media websites.

## Streamlit Cloud setup

1. Open the app in Streamlit Community Cloud.
2. Open **Manage app → Settings → Secrets**.
3. Add TOML values like:

```toml
TELEGRAM_API_ID = "your_api_id"
TELEGRAM_API_HASH = "your_api_hash"
TELEGRAM_SESSION_STRING = "your_telethon_string_session"
DATABASE_PATH = "data/newsroom.db"
REFRESH_SECONDS = "60"
```

4. Save the secrets.
5. Reboot the app.

RSS mirrors are fetched automatically by the app. Telegram requires a Telethon StringSession generated after logging in once; never put a phone code or password in the repository. If Telegram secrets are absent, X RSS monitoring still runs.

## Sources

`config/sources.yaml` contains only X RSS mirror entries and confirmed public Telegram channels for IDF, COGAT and Al-Qassam. RSS mirrors are third-party services and can be rate-limited or unavailable. Replace any mirror URL that stops working. No official X API is used.
