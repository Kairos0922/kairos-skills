#!/usr/bin/env python3
"""reddit.py - Reddit feed adapter"""

from scripts.source_adapters.base import FeedSourceAdapter


class RedditAdapter(FeedSourceAdapter):
    """
    Reddit adapter.

    当前支持 feed 形式的 Reddit 数据源，例如 subreddit / search RSS。
    """

    source_type = "reddit"
