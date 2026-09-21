"""Stable content hashing for cross-feed deduplication."""

from __future__ import annotations

import hashlib
import re


def content_hash(source: str, text: str, url: str = "") -> str:
    """Return a normalized SHA-256 hash for a post."""
    normalized = re.sub(r"\s+", " ", text).strip().casefold()
    identity = f"{source.casefold().strip()}|{normalized}|{url.strip()}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()
