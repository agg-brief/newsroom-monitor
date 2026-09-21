"""Streamlit entry point for the newsroom monitoring dashboard."""

from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config.settings import Settings
from database.repository import NewsRepository


st.set_page_config(page_title="Newsroom Monitor", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")


def format_time(value: str) -> str:
    """Format an ISO timestamp as the compact local display time."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone().strftime("%H:%M")
    except ValueError:
        return value[:5]


def post_row(post: dict[str, str]) -> str:
    """Render one complete clickable post row."""
    source = html.escape(post["source"])
    headline = html.escape(post["headline"])
    url = html.escape(post.get("url") or "#", quote=True)
    time = html.escape(format_time(post["published_at"]))
    return f'<a class="post-row" href="{url}" target="_blank" rel="noopener"><span class="post-time">{time}</span><span class="post-source">{source}</span><span class="post-headline">{headline}</span></a>'


@st.cache_resource
def get_repository(path: str) -> NewsRepository:
    return NewsRepository(path)


settings = Settings.from_env()
repository = get_repository(str(settings.database_path))
repository.initialize()
st_autorefresh(interval=settings.refresh_seconds * 1000, key="newsroom-refresh")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; max-width: 1800px; }
    .post-row { display:flex; align-items:center; gap:.75rem; padding:.52rem .7rem; margin:.18rem 0; border:1px solid rgba(128,128,128,.2); border-radius:5px; color:inherit; text-decoration:none!important; background:rgba(128,128,128,.035); transition:background .12s; }
    .post-row:hover { background:rgba(70,130,220,.15); }
    .post-time { flex:0 0 3.2rem; color:#8b949e; font-variant-numeric:tabular-nums; }
    .post-source { flex:0 0 10rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:650; }
    .post-headline { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .column-title { border-bottom:2px solid #4d8fd1; padding-bottom:.35rem; margin-bottom:.4rem; }
    @media (max-width: 700px) { .post-source { flex-basis:6rem; } .post-row { gap:.35rem; padding:.45rem .35rem; font-size:.82rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛰️ Newsroom Monitor")
st.caption(f"Live feed · refreshed every {settings.refresh_seconds} seconds · {datetime.now(timezone.utc).astimezone().strftime('%H:%M:%S')}")

posts = repository.recent(limit=settings.max_posts)
categories = settings.categories
with st.sidebar:
    st.header("Filters")
    selected_categories = st.multiselect("Categories", categories, default=categories)
    sources = sorted({post["source"] for post in posts})
    selected_sources = st.multiselect("Sources", sources, default=sources)
    search = st.text_input("Search", placeholder="Search headlines and sources…")
    if st.button("Clear filters", use_container_width=True):
        st.rerun()

filtered = [
    post for post in posts
    if post["category"] in selected_categories
    and post["source"] in selected_sources
    and (not search or search.casefold() in f'{post["headline"]} {post["source"]}'.casefold())
]

for category in categories:
    category_posts = [post for post in filtered if post["category"] == category]
    with st.container():
        st.markdown(f'<h3 class="column-title">{html.escape(category)} <small>({len(category_posts)})</small></h3>', unsafe_allow_html=True)
        if category_posts:
            st.markdown("".join(post_row(post) for post in category_posts), unsafe_allow_html=True)
        else:
            st.caption("No matching posts")

if not filtered:
    st.info("No posts match the current filters.")
