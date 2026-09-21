"""RSS collector for public feeds, including X mirrors/RSS services."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from collectors.models import Post


def _published(entry: object) -> datetime:
    raw = getattr(entry, "published", "") or getattr(entry, "updated", "")
    if not raw:
        return datetime.now(timezone.utc)
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def collect_rss(feeds: dict[str, list[str]]) -> list[Post]:
    """Collect entries keyed by category. Feed URLs must be public RSS endpoints."""
    posts: list[Post] = []
    for category, urls in feeds.items():
        for feed_url in urls:
            parsed = feedparser.parse(feed_url)
            feed_name = parsed.feed.get("title", feed_url)
            for entry in parsed.entries:
                headline = entry.get("title", "").strip()
                if not headline:
                    continue
                url = entry.get("link", "")
                external_id = entry.get("id") or url or hashlib.sha256(f"{feed_name}:{headline}".encode()).hexdigest()
                posts.append(Post.now_collected(external_id=f"rss:{external_id}", category=category, source=str(feed_name), headline=headline, url=url, published_at=_published(entry)))
    return posts
