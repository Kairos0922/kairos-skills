#!/usr/bin/env python3
"""
base.py - source adapter base classes and shared feed helpers
"""

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

import feedparser


@dataclass
class Signal:
    id: str
    type: str
    content: str
    source: dict
    relevance_score: float
    priority: str
    published_at: str

    def to_dict(self) -> dict:
        return asdict(self)


class BaseSourceAdapter:
    source_type = "base"

    def collect(
        self,
        source: dict,
        cutoff_date: datetime,
        keywords: List[str],
        context: Dict[str, Any],
    ) -> List[Signal]:
        raise NotImplementedError


class FeedSourceAdapter(BaseSourceAdapter):
    """
    通用 feed adapter。

    适用于：
    - RSS
    - Atom
    - 以 feed 形式暴露的 GitHub / Reddit / X 镜像源
    """

    def collect(
        self,
        source: dict,
        cutoff_date: datetime,
        keywords: List[str],
        context: Dict[str, Any],
    ) -> List[Signal]:
        feed = feedparser.parse(source["url"])
        signals: List[Signal] = []

        for entry in feed.entries:
            published_at = self._parse_published_at(entry)
            if not self._within_cutoff(published_at, cutoff_date):
                continue

            title = entry.get("title", "")
            content = self._extract_content(entry)
            text_to_check = (title + " " + content).lower()
            if keywords and not any(keyword.lower() in text_to_check for keyword in keywords):
                continue

            relevance_score = self._calc_relevance(title, content, keywords)
            priority = self._infer_priority(relevance_score)
            signals.append(
                Signal(
                    id=f"sig-{hashlib.md5((title + source['name']).encode()).hexdigest()[:8]}",
                    type=self._classify_content(title, content),
                    content=title + (" " + content[:200] if content else ""),
                    source={
                        "platform": source["name"],
                        "url": entry.get("link", source["url"]),
                        "author": entry.get("author", ""),
                        "collector": source["name"],
                    },
                    relevance_score=relevance_score,
                    priority=priority,
                    published_at=published_at,
                )
            )

        return signals

    def _parse_published_at(self, entry: dict) -> str:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass
        return datetime.now(timezone.utc).isoformat()

    def _within_cutoff(self, published_at: str, cutoff_date: datetime) -> bool:
        try:
            pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            return pub_dt >= cutoff_date
        except Exception:
            return True

    def _extract_content(self, entry: dict) -> str:
        content = ""
        if hasattr(entry, "summary"):
            content = entry.summary
        elif hasattr(entry, "description"):
            content = entry.description
        elif hasattr(entry, "title"):
            content = entry.title
        return re.sub(r"<[^>]+>", "", content).strip()

    def _calc_relevance(self, title: str, content: str, keywords: List[str]) -> float:
        if not keywords:
            return 0.5
        text = (title + " " + content[:500]).lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text)
        return min(1.0, matches / 3.0)

    def _infer_priority(self, relevance_score: float) -> str:
        if relevance_score > 0.7:
            return "P0"
        if relevance_score < 0.4:
            return "P2"
        return "P1"

    def _classify_content(self, title: str, content: str) -> str:
        text = (title + " " + content[:300]).lower()
        if any(keyword in text for keyword in ["announce", "release", "launch", "introducing", "发布"]):
            return "product_news"
        if any(keyword in text for keyword in ["research", "paper", "study", "发现"]):
            return "research"
        if any(keyword in text for keyword in ["tutorial", "guide", "how to", "教程"]):
            return "tutorial"
        if any(keyword in text for keyword in ["opinion", "think", "believe", "观点"]):
            return "opinion"
        return "trend"


def extract_domain_label(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host or "unknown-source"
    except Exception:
        return "unknown-source"
