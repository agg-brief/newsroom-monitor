"""TweetDeck-style Streamlit newsroom monitor."""

from __future__ import annotations

import html
import logging
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.db import Database
from utils.settings import Settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)

st.set_page_config(page_title="Newsroom Monitor", page_icon="🛰️", layout="wide")

PRIORITY_KEYWORDS = ("hostage", "ceasefire", "cabinet", "iran", "hezbollah", "rocket", "airstrike", "settlement", "evacuation", "aid")


def parse_time(value: str) -> str:
    """Return a timestamp in the compact local HH:MM format."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone().strftime("%H:%M")
    except ValueError:
        return value[:5]


def render_post(post: dict[str, object]) -> str:
    """Render a complete, keyboard-accessible, clickable post row."""
    text = str(post["text"])
    is_priority = any(keyword in text.casefold() for keyword in PRIORITY_KEYWORDS)
    priority_class = " priority" if is_priority else ""
    url = html.escape(str(post["url"] or "#"), quote=True)
    return (
        f'<a class="post{priority_class}" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<span class="time">{html.escape(parse_time(str(post["timestamp"])))}</span>'
        f'<span class="source">{html.escape(str(post["source"]))}</span>'
        f'<span class="headline">{html.escape(text)}</span></a>'
    )


@st.cache_resource
def get_database(path: str) -> Database:
    """Create one reusable database handle per Streamlit process."""
    return Database(Path(path))


settings = Settings.load()
database = get_database(settings.database_path)
database.initialize()
st_autorefresh(interval=settings.refresh_seconds * 1000, key="newsroom-refresh")

st.markdown("""
<style>
:root { color-scheme: dark; }
.block-container { max-width: 2200px; padding: .7rem .8rem 1rem; }
[data-testid="stHeader"] { background: #10151c; }
h1 { margin: 0; font-size: 1.35rem; }
.subtitle { color: #8b98a7; font-size: .78rem; margin-bottom: .55rem; }
.columns { display: grid; grid-template-columns: repeat(5, minmax(210px, 1fr)); gap: .45rem; width: 100%; }
.news-column { background: #111820; border: 1px solid #27313c; border-radius: 3px; min-width: 0; }
.column-heading { background: #18232d; border-bottom: 2px solid #3b82b8; color: #d8e3ec; font-size: .83rem; font-weight: 700; padding: .42rem .48rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.column-heading small { color: #8796a5; font-weight: 400; }
.post-list { height: calc(100vh - 155px); min-height: 300px; overflow-y: auto; overflow-x: hidden; }
.post { box-sizing: border-box; display: grid; grid-template-columns: 2.65rem 5.6rem minmax(0, 1fr); align-items: center; gap: .3rem; width: 100%; min-height: 28px; padding: .18rem .35rem; border-bottom: 1px solid #202a33; color: #dce5ec; font-size: .73rem; line-height: 1.15; text-decoration: none !important; }
.post:hover, .post:focus { background: #203747; outline: none; }
.post.priority { border-left: 3px solid #e05252; padding-left: .2rem; background: #251c20; }
.time { color: #8090a0; font-variant-numeric: tabular-nums; }
.source { color: #61b4e6; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.headline { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.empty { color: #687788; font-size: .75rem; padding: .65rem .45rem; }
@media (max-width: 1100px) { .columns { grid-template-columns: repeat(2, minmax(250px, 1fr)); } .post-list { height: 55vh; } }
@media (max-width: 650px) { .columns { grid-template-columns: 1fr; } .post-list { height: 45vh; } }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🛰️ Newsroom Monitor</h1>", unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Israel · Palestinian territories · Lebanon · region &nbsp;|&nbsp; auto-refresh {settings.refresh_seconds}s &nbsp;|&nbsp; {datetime.now(timezone.utc).astimezone():%H:%M:%S}</div>', unsafe_allow_html=True)

all_posts = database.recent(settings.max_posts)
with st.sidebar:
    st.header("Filters")
    search = st.text_input("Search", placeholder="headline or source")
    selected_categories = st.multiselect("Categories", settings.categories, default=settings.categories)
    source_names = sorted({str(post["source"]) for post in all_posts})
    selected_sources = st.multiselect("Sources", source_names, default=source_names)
    st.caption(f"{len(all_posts)} posts loaded")

filtered = [post for post in all_posts if str(post["category"]) in selected_categories and str(post["source"]) in selected_sources and (not search or search.casefold() in f'{post["source"]} {post["text"]}'.casefold())]
columns = []
for category in settings.categories:
    posts = [post for post in filtered if post["category"] == category]
    body = "".join(render_post(post) for post in posts) or '<div class="empty">No matching posts</div>'
    columns.append(f'<section class="news-column"><div class="column-heading">{html.escape(category)} <small>({len(posts)})</small></div><div class="post-list">{body}</div></section>')
st.markdown(f'<div class="columns">{"".join(columns)}</div>', unsafe_allow_html=True)
