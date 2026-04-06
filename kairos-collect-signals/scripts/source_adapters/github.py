#!/usr/bin/env python3
"""github.py - GitHub feed adapter"""

from scripts.source_adapters.base import FeedSourceAdapter


class GitHubAdapter(FeedSourceAdapter):
    """
    GitHub adapter.

    当前支持 feed 形式的 GitHub 数据源，例如：
    - releases atom
    - commits atom
    - issues/pr rss
    - trending rss
    """

    source_type = "github"
