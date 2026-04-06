#!/usr/bin/env python3
"""github_search.py - GitHub repository search adapter via gh CLI"""

import json
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List

from scripts.source_adapters.base import BaseSourceAdapter, Signal


class GitHubSearchAdapter(BaseSourceAdapter):
    source_type = "github-search"

    def collect(
        self,
        source: dict,
        cutoff_date: datetime,
        keywords: List[str],
        context: Dict[str, Any],
    ) -> List[Signal]:
        queries = self._resolve_queries(source, context)
        results: List[Signal] = []

        for query in queries:
            command = [
                "gh",
                "search",
                "repos",
                query,
                "--limit",
                str(int(source.get("limit", 5))),
                "--json",
                "name,owner,description,url,updatedAt,stargazerCount",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
            if completed.returncode != 0:
                continue
            for repo in json.loads(completed.stdout or "[]"):
                title = repo.get("name", "")
                description = repo.get("description") or ""
                text = (title + " " + description).lower()
                if keywords and not any(keyword.lower() in text for keyword in keywords):
                    continue
                updated_at = repo.get("updatedAt") or datetime.now(timezone.utc).isoformat()
                results.append(
                    Signal(
                        id=f"sig-gh-{abs(hash((query, repo.get('url', '')))) % (10 ** 8):08d}",
                        type="repository",
                        content=title + (" " + description if description else ""),
                        source={
                            "platform": "GitHub",
                            "url": repo.get("url", ""),
                            "author": (repo.get("owner") or {}).get("login", ""),
                            "collector": source["name"],
                            "query": query,
                        },
                        relevance_score=min(1.0, 0.4 + len([kw for kw in keywords if kw.lower() in text]) * 0.15) if keywords else 0.5,
                        priority="P1",
                        published_at=updated_at,
                    )
                )
        return results

    def _resolve_queries(self, source: dict, context: Dict[str, Any]) -> List[str]:
        if source.get("queries"):
            base_queries = [query for query in source["queries"] if isinstance(query, str) and query.strip()]
        else:
            query_sets = context.get("search_queries", {}).get("query_sets", {})
            base_queries = [query for query in query_sets.get(source.get("query_set", ""), []) if isinstance(query, str) and query.strip()]

        suffix = source.get("query_suffix", "").strip()
        if not suffix:
            return base_queries
        return [f"{query} {suffix}".strip() for query in base_queries]
