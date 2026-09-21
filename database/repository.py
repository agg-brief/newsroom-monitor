"""SQLite persistence and deduplication."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from collectors.models import Post


SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    headline TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    published_at TEXT NOT NULL,
    collected_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_posts_published_at ON posts(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source);
"""


class NewsRepository:
    """Small SQLite repository with uniqueness-based deduplication."""

    def __init__(self, database_path: str) -> None:
        self.path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def save_many(self, posts: Iterable[Post]) -> int:
        rows = [post.as_row() for post in posts]
        with self._connect() as connection:
            cursor = connection.executemany(
                "INSERT OR IGNORE INTO posts (external_id, category, source, headline, url, published_at, collected_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            return cursor.rowcount

    def recent(self, limit: int = 500) -> list[dict[str, str]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT category, source, headline, url, published_at FROM posts ORDER BY published_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
