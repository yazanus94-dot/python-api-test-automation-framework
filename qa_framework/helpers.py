"""Shared helpers: redaction, data factories and health polling."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

import requests

SENSITIVE_KEYS = {"password", "access_token", "token", "refresh_token", "authorization", "secret"}


def redact(value: Any) -> Any:
    """Recursively mask credential-like keys and Bearer tokens."""
    if isinstance(value, Mapping):
        return {
            key: ("***REDACTED***" if str(key).lower() in SENSITIVE_KEYS else redact(item))
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str) and value.lower().startswith("bearer "):
        return "Bearer ***REDACTED***"
    return value


def unique_payload(prefix: str = "automation") -> dict[str, str]:
    """Deterministic-but-unique task payload; no random global state."""
    unique = f"{prefix}-{time.time_ns()}"
    return {
        "title": f"{unique[:60]}",
        "description": f"Created by API automation framework: {unique[:80]}",
        "status": "pending",
    }


def wait_for_health(base_url: str, timeout: int = 20) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"API did not become healthy at {base_url}: {last_error}")
