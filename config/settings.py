"""Application configuration loaded from environment variables."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_CATEGORIES = [
    "Israeli Government",
    "Israeli Security",
    "Palestinian Authority",
    "Palestinian Factions",
    "Media & Journalists",
]


@dataclass(frozen=True)
class Settings:
    database_path: Path
    refresh_seconds: int
    max_posts: int
    categories: list[str]
    telegram_api_id: int | None
    telegram_api_hash: str | None
    telegram_session: str
    telegram_channels: list[str]
    rss_feeds: dict[str, list[str]]

    @classmethod
    def from_env(cls) -> "Settings":
        raw_feeds = os.getenv("RSS_FEEDS_JSON", "{}")
        try:
            feeds = json.loads(raw_feeds)
        except json.JSONDecodeError as exc:
            raise ValueError("RSS_FEEDS_JSON must contain valid JSON") from exc
        return cls(
            database_path=Path(os.getenv("DATABASE_PATH", "data/newsroom.db")),
            refresh_seconds=max(10, int(os.getenv("REFRESH_SECONDS", "60"))),
            max_posts=max(1, int(os.getenv("MAX_POSTS", "500"))),
            categories=json.loads(os.getenv("CATEGORIES_JSON", json.dumps(DEFAULT_CATEGORIES))),
            telegram_api_id=int(os.environ["TELEGRAM_API_ID"]) if os.getenv("TELEGRAM_API_ID") else None,
            telegram_api_hash=os.getenv("TELEGRAM_API_HASH"),
            telegram_session=os.getenv("TELEGRAM_SESSION", "newsroom_monitor"),
            telegram_channels=[item.strip() for item in os.getenv("TELEGRAM_CHANNELS", "").split(",") if item.strip()],
            rss_feeds={str(key): list(value) for key, value in feeds.items()},
        )
