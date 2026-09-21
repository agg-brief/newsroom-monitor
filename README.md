# Newsroom Monitor on Streamlit Community Cloud

This app runs online on Streamlit Community Cloud and automatically fetches the configured public RSS feeds. No local computer, paid API, official X API, AWS service, or cloud database is required for RSS monitoring.

## Deploy

1. Make sure the repository is public.
2. Open <https://share.streamlit.io>.
3. Click **New app**.
4. Select `agg-brief/newsroom-monitor`, branch `main`, and file `app.py`.
5. Click **Deploy**.
6. Wait for the build to complete, then open the app URL.

The app syncs RSS during startup and on each 60-second refresh. It stores data in SQLite on the running Streamlit instance and deduplicates entries. Streamlit Cloud storage is ephemeral, so a restart can clear the local database; this is a limitation of the free platform.

## Sources

Edit `config/sources.yaml` to add public RSS feeds. The current configuration includes Israel MFA, WAFA, UN News Middle East, Jerusalem Post, Times of Israel, i24NEWS, Haaretz, Reuters, Al Jazeera, L'Orient Today, and Naharnet. X accounts require public RSS mirror URLs because this project does not use the official X API.

## Telegram

Telegram is not automatically collected on Streamlit Cloud because Telethon's first login requires an interactive phone/code flow and the free app filesystem is not durable. RSS monitoring works online immediately. Telegram can be added later by creating a Telethon session locally and securely deploying it, but it is optional.

## Reboot after a change

In Streamlit Cloud, open the app, click **Manage app**, then choose **Reboot app** or **Redeploy**. A GitHub commit normally triggers a redeploy automatically.
