#!/usr/bin/env python3
"""rss.py - RSS/Atom adapter"""

from scripts.source_adapters.base import FeedSourceAdapter


class RSSAdapter(FeedSourceAdapter):
    source_type = "rss"
