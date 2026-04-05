#!/usr/bin/env python3
"""
collector.py - 信号采集器

从配置的数据源（RSS）采集信号。
"""

import feedparser
import json
import hashlib
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import List, Optional


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


class SignalCollector:
    """从 RSS 源采集信号"""

    def __init__(self, sources_path: Optional[str] = None):
        if sources_path is None:
            skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sources_path = os.path.join(skill_dir, "references", "sources.json")

        with open(sources_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.sources = data.get("sources", [])

        # 默认关键词（与 SKILL.md 中的 default_keywords 保持一致）
        self.default_keywords = [
            "LLM", "RAG", "LangChain", "AI Agent", "Agentic AI",
            "machine learning", "neural network", "embedding",
            "Claude", "GPT", "Gemini", "Llama", "transformer",
            "prompt engineering", "fine-tuning", "RLHF",
            "vector database", "embedding", "pinecone", "weaviate",
            "AI coding", "cursor", "copilot", "aider",
            "vibe coding", "MCP", "model context protocol",
            "LangGraph", "LlamaIndex", "dspy"
        ]

    def collect_all(self, tier_filter: int = 1) -> List[Signal]:
        """
        从所有启用的源采集信号。

        Args:
            tier_filter: 只采集 >= 此 tier 的源 (1 或 2)

        Returns:
            Signal 对象列表
        """
        signals = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=3)

        for source in self.sources:
            if not source.get("enabled", True):
                continue
            if source.get("tier", 2) > tier_filter:
                continue

            try:
                source_signals = self._fetch_feed(source, cutoff_date)
                signals.extend(source_signals)
            except Exception:
                # 单个源失败不影响整体
                continue

        # 去重（基于内容哈希）
        seen = set()
        deduped = []
        for sig in signals:
            content_hash = hashlib.md5(sig.content.encode()).hexdigest()[:8]
            if content_hash not in seen:
                seen.add(content_hash)
                deduped.append(sig)

        return deduped

    def _fetch_feed(self, source: dict, cutoff_date: datetime) -> List[Signal]:
        """获取单个 RSS 源"""
        feed = feedparser.parse(source["url"])

        signals = []
        for entry in feed.entries:
            # 解析发布时间
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    published_at = dt.isoformat()
                except Exception:
                    published_at = datetime.now(timezone.utc).isoformat()
            else:
                published_at = datetime.now(timezone.utc).isoformat()

            # 检查是否在 3 天内
            try:
                pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                if pub_dt < cutoff_date:
                    continue
            except Exception:
                pass

            # 提取内容
            content = ""
            if hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description
            elif hasattr(entry, "title"):
                content = entry.title

            # 清理 HTML
            import re
            content = re.sub(r"<[^>]+>", "", content).strip()
            title = entry.get("title", "")

            # 关键词过滤
            text_to_check = (title + " " + content).lower()
            if not any(kw.lower() in text_to_check for kw in self.default_keywords):
                continue

            # 计算相关性分数（简单基于标题匹配度）
            relevance_score = self._calc_relevance(title, content)

            # 确定优先级
            priority = "P1"
            if relevance_score > 0.7:
                priority = "P0"
            elif relevance_score < 0.4:
                priority = "P2"

            signal = Signal(
                id=f"sig-{hashlib.md5((title + source['name']).encode()).hexdigest()[:8]}",
                type=self._classify_content(title, content),
                content=title + (" " + content[:200] if content else ""),
                source={
                    "platform": source["name"],
                    "url": entry.get("link", source["url"]),
                    "author": entry.get("author", "")
                },
                relevance_score=relevance_score,
                priority=priority,
                published_at=published_at
            )
            signals.append(signal)

        return signals

    def _calc_relevance(self, title: str, content: str) -> float:
        """简单计算相关性分数"""
        text = (title + " " + content[:500]).lower()
        matches = sum(1 for kw in self.default_keywords if kw.lower() in text)
        return min(1.0, matches / 3.0)

    def _classify_content(self, title: str, content: str) -> str:
        """简单分类内容类型"""
        text = (title + " " + content[:300]).lower()

        if any(kw in text for kw in ["announce", "release", "launch", "introducing", "发布"]):
            return "product_news"
        elif any(kw in text for kw in ["research", "paper", "study", "发现"]):
            return "research"
        elif any(kw in text for kw in ["tutorial", "guide", "how to", "教程"]):
            return "tutorial"
        elif any(kw in text for kw in ["opinion", "think", "believe", "观点"]):
            return "opinion"
        else:
            return "trend"
