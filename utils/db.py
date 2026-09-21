"""SQLite persistence layer."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)


class Database:
    """SQLite database with content-hash deduplication."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        """Open a configured SQLite connection."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def initialize(self) -> None:
        """Create the schema and indexes."""
        schema = Path(__file__).parents[1] / "database" / "schema.sql"
        with self.connect() as connection:
            connection.executescript(schema.read_text(encoding="utf-8"))

    def save_many(self, posts: Iterable[dict[str, object]]) -> int:
        """Insert posts, ignoring duplicate content hashes."""
        rows = [(p["source"], p["category"], p["timestamp"], p["text"], p["url"], p["language"], p["platform"], p["content_hash"]) for p in posts]
        if not rows:
            return 0
        with self.connect() as connection:
            before = connection.total_changes
            connection.executemany("INSERT OR IGNORE INTO posts (source, category, timestamp, text, url, language, platform, content_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
            return connection.total_changes - before

    def recent(self, limit: int = 1000) -> list[dict[str, object]]:
        """Return newest posts first."""
        with self.connect() as connection:
            rows = connection.execute("SELECT source, category, timestamp, text, url, language, platform FROM posts ORDER BY timestamp DESC, id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
