#!/usr/bin/env python3
"""
collector.py - 信号采集器

从领域配置的数据源采集信号。
当前采集器基于 adapter 架构，按 `sources.json` 中的 `type` 分发：
- rss
- github
- reddit
- x

说明：
- 以上 4 类目前都通过 feed 形式接入
- 如果某个平台需要原生 API / 鉴权，应新增独立 adapter，而不是继续堆在 collector.py
"""

import hashlib
import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from scripts.domain_config import DEFAULT_DOMAIN, load_keywords, load_sources
from scripts.source_adapters.base import Signal
from scripts.source_adapters.registry import get_adapter


class SignalCollector:
    """按 source adapter 分发的数据源采集器"""

    def __init__(self, domain: str = DEFAULT_DOMAIN, sources_path: Optional[str] = None):
        self.domain = domain
        if sources_path is None:
            data = load_sources(domain)
        else:
            with open(sources_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        self.sources = data.get("sources", [])

        self.default_keywords: List[str] = []
        self.recency_days = 3
        keywords_data = load_keywords(domain)
        self.default_keywords = keywords_data.get("default_keywords", self.default_keywords)
        self.recency_days = int(keywords_data.get("recency_days", self.recency_days))

    def collect_all(self, tier_filter: int = 1) -> List[Signal]:
        """
        从所有启用的源采集信号。

        Args:
            tier_filter: 只采集 >= 此 tier 的源 (1 或 2)

        Returns:
            Signal 对象列表
        """
        signals: List[Signal] = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.recency_days)

        for source in self.sources:
            if not source.get("enabled", True):
                continue
            if source.get("tier", 2) > tier_filter:
                continue

            try:
                adapter = get_adapter(source.get("type", "rss"))
                source_signals = adapter.collect(source, cutoff_date, self.default_keywords)
                signals.extend(source_signals)
            except Exception:
                # 单个源失败不影响整体
                continue

        return self._dedupe_signals(signals)

    def _dedupe_signals(self, signals: List[Signal]) -> List[Signal]:
        seen = set()
        deduped: List[Signal] = []
        for signal in signals:
            content_hash = hashlib.md5(signal.content.encode()).hexdigest()[:8]
            if content_hash not in seen:
                seen.add(content_hash)
                deduped.append(signal)
        return deduped
