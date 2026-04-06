#!/usr/bin/env python3
"""runtime_env.py - runtime environment helpers"""

import os


def get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable not set: {name}")
    return value
