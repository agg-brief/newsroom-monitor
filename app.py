"""Streamlit Cloud newsroom dashboard for X RSS mirrors and Telegram."""

from __future__ import annotations

import asyncio
import html
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from collectors.collector_rss import collect_rss
from collectors.collector_telegram import collect_telegram
from utils.db import Database
from utils.settings import Settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)
st.set_page_config(page_title="Newsroom Monitor", page_icon="🛰️", layout="wide")
PRIORITY_KEYWORDS = ("hostage", "ceasefire", "cabinet", "iran", "hezbollah", "rocket", "airstrike", "settlement", "evacuation", "aid")


def format_time(value: str) -> str:
    """Format an ISO timestamp in local HH:MM format."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone().strftime("%H:%M")
    except ValueError:
        return value[:5]


def render_post(post: dict[str, object]) -> str:
    """Render a compact clickable row."""
    text = str(post["text"])
    priority = " priority" if any(word in text.casefold() for word in PRIORITY_KEYWORDS) else ""
    url = html.escape(str(post.get("url") or "#"), quote=True)
    return (f'<a class="post{priority}" href="{url}" target="_blank" rel="noopener noreferrer">'
            f'<span class="time">{html.escape(format_time(str(post["timestamp"])))}</span>'
            f'<span class="source">{html.escape(str(post["source"]))}</span>'
            f'<span class="headline">{html.escape(text)}</span></a>')


@st.cache_resource
def get_database(path: str) -> Database:
    """Create one database object for the Streamlit process."""
    return Database(Path(path))


settings = Settings.load()
database = get_database(settings.database_path)
database.initialize()
st_autorefresh(interval=settings.refresh_seconds * 1000, key="newsroom-refresh")
now = time.time()
if now - float(st.session_state.get("last_sync", 0.0)) >= settings.refresh_seconds:
    try:
        entries = collect_rss(settings.rss_sources())
        if settings.telegram_api_id and settings.telegram_api_hash and settings.telegram_sources():
            entries.extend(asyncio.run(collect_telegram(settings.telegram_api_id, settings.telegram_api_hash, settings.telegram_session, settings.telegram_sources(), session_string=settings.telegram_session_string)))
        inserted = database.save_many(entries)
        LOGGER.info("sync: %d fetched, %d inserted", len(entries), inserted)
    except Exception:  # noqa: BLE001
        LOGGER.exception("source sync failed")
    st.session_state.last_sync = now

st.markdown("""
<style>
:root { color-scheme: dark; }.block-container { max-width:2200px; padding:.7rem .8rem 1rem; } h1{margin:0;font-size:1.35rem}.subtitle{color:#8b98a7;font-size:.78rem;margin-bottom:.55rem}.columns{display:grid;grid-template-columns:repeat(5,minmax(210px,1fr));gap:.45rem}.news-column{background:#111820;border:1px solid #27313c;border-radius:3px;min-width:0}.column-heading{background:#18232d;border-bottom:2px solid #3b82b8;color:#d8e3ec;font-size:.83rem;font-weight:700;padding:.42rem .48rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.column-heading small{color:#8796a5;font-weight:400}.post-list{height:calc(100vh - 155px);min-height:300px;overflow-y:auto}.post{display:grid;grid-template-columns:2.65rem 7rem minmax(0,1fr);align-items:center;gap:.3rem;min-height:28px;padding:.18rem .35rem;border-bottom:1px solid #202a33;color:#dce5ec;font-size:.73rem;line-height:1.15;text-decoration:none!important}.post:hover,.post:focus{background:#203747;outline:none}.post.priority{border-left:3px solid #e05252;padding-left:.2rem;background:#251c20}.time{color:#8090a0;font-variant-numeric:tabular-nums}.source{color:#61b4e6;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.headline{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.empty{color:#687788;font-size:.75rem;padding:.65rem .45rem}@media(max-width:1100px){.columns{grid-template-columns:repeat(2,minmax(250px,1fr))}.post-list{height:55vh}}@media(max-width:650px){.columns{grid-template-columns:1fr}.post-list{height:45vh}}
</style>
""", unsafe_allow_html=True)
st.markdown("<h1>🛰️ Newsroom Monitor</h1>", unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">X RSS mirrors + Telegram · refreshes every {settings.refresh_seconds}s · {datetime.now(timezone.utc).astimezone():%H:%M:%S}</div>', unsafe_allow_html=True)
posts = database.recent(settings.max_posts)
with st.sidebar:
    st.header("Filters")
    search = st.text_input("Search", placeholder="headline or source")
    selected_categories = st.multiselect("Categories", settings.categories, default=settings.categories)
    source_names = sorted({str(post["source"]) for post in posts})
    selected_sources = st.multiselect("Sources", source_names, default=source_names)
    st.caption(f"{len(posts)} posts loaded")
filtered = [post for post in posts if str(post["category"]) in selected_categories and str(post["source"]) in selected_sources and (not search or search.casefold() in f'{post["source"]} {post["text"]}'.casefold())]
columns = []
for category in settings.categories:
    category_posts = [post for post in filtered if post["category"] == category]
    body = "".join(render_post(post) for post in category_posts) or '<div class="empty">No matching posts</div>'
    columns.append(f'<section class="news-column"><div class="column-heading">{html.escape(category)} <small>({len(category_posts)})</small></div><div class="post-list">{body}</div></section>')
st.markdown(f'<div class="columns">{"".join(columns)}</div>', unsafe_allow_html=True)
