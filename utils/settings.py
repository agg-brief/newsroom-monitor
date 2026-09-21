"""Environment and YAML-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()
CATEGORIES = ["Israeli Government", "Israeli Security", "Palestinian Authority", "Palestinian Factions", "Media & Journalists"]


@dataclass(frozen=True)
class Settings:
    """Runtime settings and source configuration."""

    database_path: str
    refresh_seconds: int
    max_posts: int
    categories: list[str]
    sources: list[dict[str, Any]]
    telegram_api_id: int | None
    telegram_api_hash: str | None
    telegram_session: str
    telegram_session_string: str | None

    @classmethod
    def load(cls) -> "Settings":
        """Load environment variables and config/sources.yaml."""
        config_path = Path(os.getenv("SOURCES_CONFIG", "config/sources.yaml"))
        raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        raw = raw or {}
        return cls(
            database_path=os.getenv("DATABASE_PATH", "data/newsroom.db"),
            refresh_seconds=max(10, int(os.getenv("REFRESH_SECONDS", "60"))),
            max_posts=max(50, int(os.getenv("MAX_POSTS", "1000"))),
            categories=list(raw.get("categories", CATEGORIES)),
            sources=[item for item in raw.get("sources", []) if isinstance(item, dict)],
            telegram_api_id=int(os.environ["TELEGRAM_API_ID"]) if os.getenv("TELEGRAM_API_ID") else None,
            telegram_api_hash=os.getenv("TELEGRAM_API_HASH"),
            telegram_session=os.getenv("TELEGRAM_SESSION", "data/newsroom_monitor"),
            telegram_session_string=os.getenv("TELEGRAM_SESSION_STRING") or None,
        )

    def rss_sources(self) -> list[dict[str, Any]]:
        """Return configured RSS mirrors."""
        return [source for source in self.sources if source.get("platform") == "rss" and str(source.get("url", "")).startswith("http")]

    def telegram_sources(self) -> list[dict[str, Any]]:
        """Return configured public Telegram channels."""
        return [source for source in self.sources if source.get("platform") == "telegram" and source.get("channel")]
