#!/usr/bin/env python3
"""tavily.py - Tavily search adapter"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib import request

from scripts.runtime_env import get_required_env
from scripts.source_adapters.base import BaseSourceAdapter, Signal, extract_domain_label


TAVILY_URL = "https://api.tavily.com/search"


class TavilyAdapter(BaseSourceAdapter):
    source_type = "tavily"

    def collect(
        self,
        source: dict,
        cutoff_date: datetime,
        keywords: List[str],
        context: Dict[str, Any],
    ) -> List[Signal]:
        api_key = get_required_env("TAVILY_API_KEY")
        queries = self._resolve_queries(source, context)
        signals: List[Signal] = []

        for query in queries:
            payload = {
                "query": query,
                "api_key": api_key,
                "max_results": int(source.get("max_results", 5)),
                "search_depth": source.get("search_depth", "basic"),
            }
            if source.get("include_domains"):
                payload["include_domains"] = source["include_domains"]
            if source.get("exclude_domains"):
                payload["exclude_domains"] = source["exclude_domains"]

            req = request.Request(
                TAVILY_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=20) as response:
                data = json.loads(response.read())
            for item in data.get("results", []):
                url = item.get("url", "")
                title = item.get("title", "")
                content = item.get("content", "")[:240]
                text = (title + " " + content).lower()
                if keywords and not any(keyword.lower() in text for keyword in keywords):
                    continue
                signals.append(
                    Signal(
                        id=f"sig-tavily-{abs(hash((query, url))) % (10 ** 8):08d}",
                        type="search_result",
                        content=title + (" " + content if content else ""),
                        source={
                            "platform": extract_domain_label(url),
                            "url": url,
                            "author": "",
                            "collector": source["name"],
                            "query": query,
                        },
                        relevance_score=min(1.0, 0.5 + text.count(query.lower()) * 0.1),
                        priority="P1",
                        published_at=datetime.now(timezone.utc).isoformat(),
                    )
                )
        return signals

    def _resolve_queries(self, source: dict, context: Dict[str, Any]) -> List[str]:
        if source.get("queries"):
            return [query for query in source["queries"] if isinstance(query, str) and query.strip()]
        query_sets = context.get("search_queries", {}).get("query_sets", {})
        query_set = source.get("query_set", "")
        queries = query_sets.get(query_set, [])
        query_template = source.get("query_template", "{query}")
        return [query_template.format(query=query) for query in queries if isinstance(query, str) and query.strip()]
