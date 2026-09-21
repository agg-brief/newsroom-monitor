"""Public Telegram collector implemented with Telethon."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from telethon import TelegramClient
from telethon.sessions import StringSession

from utils.hashing import content_hash

LOGGER = logging.getLogger(__name__)


async def collect_telegram(api_id: int, api_hash: str, session: str, sources: list[dict[str, Any]], limit: int = 100, session_string: str | None = None) -> list[dict[str, object]]:
    """Collect recent messages from public channels using a file or StringSession."""
    session_spec: str | StringSession = StringSession(session_string) if session_string else session
    posts: list[dict[str, object]] = []
    async with TelegramClient(session_spec, api_id, api_hash) as client:
        for source in sources:
            channel = str(source["channel"])
            try:
                entity = await client.get_entity(channel)
                async for message in client.iter_messages(entity, limit=limit):
                    text = (message.message or "").strip().replace("\n", " ")
                    if not text:
                        continue
                    timestamp = (message.date or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
                    url = f"https://t.me/{channel.lstrip('@')}/{message.id}"
                    name = str(source.get("name", channel))
                    posts.append({"source": name, "category": str(source["category"]), "timestamp": timestamp, "text": text, "url": url, "language": str(source.get("language", "und")), "platform": "telegram", "content_hash": content_hash(name, text, url)})
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unable to collect Telegram channel %s", channel)
    return posts
