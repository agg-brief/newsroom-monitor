"""Telethon collector for public Telegram channels."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from telethon import TelegramClient

from collectors.models import Post


async def collect_telegram(api_id: int, api_hash: str, session: str, channels: list[str], category_by_channel: dict[str, str]) -> list[Post]:
    """Fetch recent public messages. A Telethon session file is persisted locally."""
    posts: list[Post] = []
    async with TelegramClient(session, api_id, api_hash) as client:
        for channel in channels:
            entity = await client.get_entity(channel)
            source = getattr(entity, "title", channel)
            category = category_by_channel.get(channel, "Media & Journalists")
            async for message in client.iter_messages(entity, limit=100):
                text = (message.message or "").strip().replace("\n", " ")
                if not text:
                    continue
                url = f"https://t.me/{channel.lstrip('@')}/{message.id}"
                external_id = hashlib.sha256(f"telegram:{channel}:{message.id}".encode()).hexdigest()
                published = message.date or datetime.now(timezone.utc)
                posts.append(Post.now_collected(external_id=external_id, category=category, source=source, headline=text, url=url, published_at=published))
    return posts
