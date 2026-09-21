"""Collector data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Post:
    external_id: str
    category: str
    source: str
    headline: str
    url: str
    published_at: str
    collected_at: str

    @classmethod
    def now_collected(cls, *, external_id: str, category: str, source: str, headline: str, url: str, published_at: datetime) -> "Post":
        return cls(external_id, category, source, headline.strip(), url, published_at.astimezone(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat())

    def as_row(self) -> tuple[str, ...]:
        return (self.external_id, self.category, self.source, self.headline, self.url, self.published_at, self.collected_at)
