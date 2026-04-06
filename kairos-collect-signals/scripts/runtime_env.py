#!/usr/bin/env python3
"""runtime_env.py - runtime environment helpers

提供安全的密钥读取：优先读取环境变量，其次读取本地系统钥匙串（keyring）。

约定：
- 服务名（service）固定为 `kairos-collect-signals`
- 凭据用户名（username）是环境变量名的小写，例如 `TAVILY_API_KEY` -> `tavily_api_key`

第一次使用时，如果没有提供 `TAVILY_API_KEY`，请运行：
    python3 scripts/setup_tavily_key.py
"""

import os
from typing import Optional


SERVICE_NAME = "kairos-collect-signals"


def _get_from_keyring(name: str) -> Optional[str]:
    """Read secret from OS keyring if available. Return None on any error."""
    try:
        import keyring  # type: ignore
    except Exception:
        return None

    try:
        value = keyring.get_password(SERVICE_NAME, name.lower())
        if value:
            return value.strip()
        return None
    except Exception:
        return None


def get_required_env(name: str) -> str:
    """Read secret by name, preferring env var then keyring.

    Raises RuntimeError with a helpful instruction when missing.
    """
    value = os.environ.get(name, "").strip()
    if value:
        return value

    # fallback to keyring
    value = _get_from_keyring(name) or ""
    if value:
        return value

    raise RuntimeError(
        (
            f"required secret not found: {name}. "
            f"Set environment variable {name} or store it via OS keychain: "
            f"python3 scripts/setup_tavily_key.py"
        )
    )
