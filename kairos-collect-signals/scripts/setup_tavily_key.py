#!/usr/bin/env python3
"""setup_tavily_key.py - Store Tavily API key in the OS keychain

Usage:
  python3 scripts/setup_tavily_key.py

This script stores `TAVILY_API_KEY` into your operating system's keychain via
the `keyring` library. The skill will read the key at runtime using
`keyring.get_password(service, username)` with:

- service: "kairos-collect-signals"
- username: "tavily_api_key"  (lowercased env name)

If the environment variable `TAVILY_API_KEY` is set when you run this script,
the value will be used directly; otherwise you'll be prompted to paste the key.
"""

import getpass
import os
import sys


SERVICE = "kairos-collect-signals"
USERNAME = "tavily_api_key"


def main() -> None:
    try:
        import keyring  # type: ignore
    except Exception:
        print(
            "Error: Python package 'keyring' is required. Install it with: pip install keyring",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        print("Enter your Tavily API key. Input will be hidden.")
        api_key = getpass.getpass(prompt="TAVILY_API_KEY: ").strip()

    if not api_key:
        print("No key provided. Aborting.", file=sys.stderr)
        sys.exit(1)

    try:
        keyring.set_password(SERVICE, USERNAME, api_key)
    except Exception as e:
        print(f"Failed to store key in OS keychain: {e}", file=sys.stderr)
        sys.exit(1)

    print(
        "TAVILY_API_KEY stored in OS keychain. The skill can now access it without .env files."
    )


if __name__ == "__main__":
    main()

