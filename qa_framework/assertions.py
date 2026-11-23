"""Reusable API assertions and JSON Schema validation."""

from __future__ import annotations

from typing import Any

import jsonschema
import requests


def assert_status(response: requests.Response, expected: int) -> None:
    assert (
        response.status_code == expected
    ), f"Expected {expected}, got {response.status_code}: {response.text[:300]}"


def assert_json_content_type(response: requests.Response) -> None:
    assert response.headers.get("Content-Type", "").startswith(
        "application/json"
    ), f"Expected JSON content type, got {response.headers.get('Content-Type')}"


def assert_fields(body: dict[str, Any], required: set[str]) -> None:
    missing = required - set(body)
    assert not missing, f"Missing required response fields: {sorted(missing)}"


def assert_error_body(
    response: requests.Response, expected_code: str | None = None
) -> dict[str, Any]:
    body = response.json()
    assert isinstance(body, dict)
    assert isinstance(body.get("detail"), (str, list))
    if expected_code is not None:
        assert body.get("code") == expected_code, body
    return body


def validate_schema(instance: Any, schema: dict[str, Any]) -> None:
    jsonschema.validate(instance=instance, schema=schema)
