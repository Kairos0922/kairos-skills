#!/usr/bin/env python3
"""
CLI entry point for style routing.

Calls shared/router.py for core logic.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.router import resolve_style, load_registry
from shared.platform import normalize_usage, get_ratio, detect_language
from shared.intake import parse_input


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: select_style.py <user_input>")
        print("Example: select_style.py '帮我做一张小红书封面，主题是用户增长飞轮'")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])

    # Parse input
    topic, raw_usage = parse_input(user_input)
    usage = normalize_usage(raw_usage) if raw_usage else ""
    ratio = get_ratio(usage) if usage else "4:5"
    language = detect_language(topic)

    # Load registry
    styles_dir = Path(__file__).parent.parent / "styles"
    registry = load_registry(styles_dir)

    # Resolve style
    style_id, confidence = resolve_style(user_input, registry)

    # Output result
    print(f"Topic: {topic}")
    print(f"Usage: {usage or '(not specified)'}")
    print(f"Ratio: {ratio}")
    print(f"Language: {language}")
    print(f"Style: {style_id or '(not determined)'}")
    print(f"Confidence: {confidence}%")

    if style_id is None:
        print("\n⚠️  Cannot determine style. Clarification needed.")
        print("Question: 你想要什么风格？商业分析风 / 杂志编辑风 / 现代艺术风？")
    elif confidence < 50:
        print(f"\n⚠️  Low confidence ({confidence}%). Consider clarifying with user.")
    else:
        print(f"\n✅ Style resolved: {style_id}")


if __name__ == "__main__":
    main()
