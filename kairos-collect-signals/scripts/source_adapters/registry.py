#!/usr/bin/env python3
"""registry.py - source adapter registry"""

from scripts.source_adapters.base import BaseSourceAdapter
from scripts.source_adapters.github_search import GitHubSearchAdapter
from scripts.source_adapters.github import GitHubAdapter
from scripts.source_adapters.reddit import RedditAdapter
from scripts.source_adapters.rss import RSSAdapter
from scripts.source_adapters.tavily import TavilyAdapter
from scripts.source_adapters.x import XAdapter


ADAPTERS = {
    "rss": RSSAdapter(),
    "github": GitHubAdapter(),
    "github-search": GitHubSearchAdapter(),
    "reddit": RedditAdapter(),
    "tavily": TavilyAdapter(),
    "x": XAdapter(),
}


def get_adapter(source_type: str) -> BaseSourceAdapter:
    normalized = (source_type or "rss").strip().lower()
    if normalized not in ADAPTERS:
        raise ValueError(f"unsupported source adapter type: {source_type}")
    return ADAPTERS[normalized]
