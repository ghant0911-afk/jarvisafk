from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# Load .env file if exists
try:
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
except Exception:
    pass


def _proxy_url() -> Optional[str]:
    explicit = os.getenv("TELEGRAM_PROXY_URL", "").strip()
    if explicit:
        return explicit

    host = os.getenv("TELEGRAM_PROXY_HOST", "").strip()
    port = os.getenv("TELEGRAM_PROXY_PORT", "").strip()
    user = os.getenv("TELEGRAM_PROXY_USER", "").strip()
    password = os.getenv("TELEGRAM_PROXY_PASS", "").strip()
    scheme = os.getenv("TELEGRAM_PROXY_SCHEME", "socks5h").strip() or "socks5h"

    if host and port and user and password:
        return f"{scheme}://{user}:{password}@{host}:{port}"
    if host and port:
        return f"{scheme}://{host}:{port}"
    return None


def get_proxies() -> Optional[Dict[str, str]]:
    proxy = _proxy_url()
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def telegram_api(token: str, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = params or {}
    url = f"https://api.telegram.org/bot{token}/{method}"
    proxies = get_proxies()
    if method == "getUpdates":
        response = requests.get(url, params=params, timeout=40, proxies=proxies)
    else:
        response = requests.post(url, json=params, timeout=20, proxies=proxies)
    response.raise_for_status()
    return response.json()


def download_file(url: str) -> bytes:
    response = requests.get(url, timeout=40, proxies=get_proxies())
    response.raise_for_status()
    return response.content
