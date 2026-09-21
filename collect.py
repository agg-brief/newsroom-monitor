"""Run RSS and Telegram collectors and persist normalized posts."""

from __future__ import annotations

import asyncio
import logging

from collectors.collector_rss import collect_rss
from collectors.collector_telegram import collect_telegram
from utils.db import Database
from utils.settings import Settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Collect all configured sources without failing the complete run on one source."""
    settings = Settings.load()
    database = Database(__import__("pathlib").Path(settings.database_path))
    database.initialize()
    posts = collect_rss(settings.rss_sources())
    if settings.telegram_api_id and settings.telegram_api_hash and settings.telegram_sources():
        posts.extend(asyncio.run(collect_telegram(settings.telegram_api_id, settings.telegram_api_hash, settings.telegram_session, settings.telegram_sources())))
    elif settings.telegram_sources():
        LOGGER.warning("Telegram sources configured but TELEGRAM_API_ID/API_HASH are missing")
    LOGGER.info("Collected %d posts; inserted %d new posts", len(posts), database.save_many(posts))


if __name__ == "__main__":
    main()
