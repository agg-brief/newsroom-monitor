"""RSS feed collector."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser

from utils.hashing import content_hash

LOGGER = logging.getLogger(__name__)


def published_at(entry: Any) -> str:
    """Extract an ISO timestamp from a feed entry, falling back to now."""
    stamp = entry.get("published") or entry.get("updated")
    if not stamp:
        return datetime.now(timezone.utc).isoformat()
    try:
        return parsedate_to_datetime(stamp).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError):
        return datetime.now(timezone.utc).isoformat()


def collect_rss(sources: list[dict[str, Any]]) -> list[dict[str, object]]:
    """Read configured RSS sources and normalize entries."""
    posts: list[dict[str, object]] = []
    for source in sources:
        try:
            feed = feedparser.parse(str(source["url"]))
            if getattr(feed, "bozo", False):
                LOGGER.warning("Feed parser warning for %s: %s", source.get("name"), getattr(feed, "bozo_exception", "unknown"))
            for entry in feed.entries:
                text = str(entry.get("title", "")).strip()
                if not text:
                    continue
                url = str(entry.get("link", source["url"]))
                name = str(source.get("name", feed.feed.get("title", source["url"])))
                posts.append({"source": name, "category": str(source["category"]), "timestamp": published_at(entry), "text": text.replace("\n", " "), "url": url, "language": str(source.get("language", "und")), "platform": "rss", "content_hash": content_hash(name, text, url)})
        except Exception:  # noqa: BLE001 - one broken feed must not stop collection
            LOGGER.exception("Unable to collect RSS source %s", source.get("name"))
    return posts
