"""CLI ingestion job for cron/systemd or manual runs."""

from __future__ import annotations

import asyncio

from collectors.rss import collect_rss
from collectors.telegram import collect_telegram
from config.settings import Settings
from database.repository import NewsRepository


def main() -> None:
    settings = Settings.from_env()
    repository = NewsRepository(str(settings.database_path))
    repository.initialize()
    posts = collect_rss(settings.rss_feeds)
    if settings.telegram_api_id and settings.telegram_api_hash and settings.telegram_channels:
        posts.extend(asyncio.run(collect_telegram(settings.telegram_api_id, settings.telegram_api_hash, settings.telegram_session, settings.telegram_channels, {})))
    added = repository.save_many(posts)
    print(f"Collected {len(posts)} posts; inserted {added} new posts.")


if __name__ == "__main__":
    main()
