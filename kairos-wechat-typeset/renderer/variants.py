"""Variant guardrails for theme components."""

from __future__ import annotations

from typing import Any, Dict, List


def variant_findings(theme: Dict[str, Any]) -> List[str]:
    findings: List[str] = []
    for component, spec in theme.get("components", {}).items():
        variants = spec.get("variants", [])
        if len(variants) > 3:
            findings.append(f"Component '{component}' defines {len(variants)} variants; maximum is 3.")
    return findings

