#!/usr/bin/env python3
"""x.py - X feed adapter"""

from scripts.source_adapters.base import FeedSourceAdapter


class XAdapter(FeedSourceAdapter):
    """
    X adapter.

    当前支持 feed 形式的数据源，例如 RSSHub / 第三方桥接后的 feed。
    不直接处理原生 x.com API 鉴权。
    """

    source_type = "x"
