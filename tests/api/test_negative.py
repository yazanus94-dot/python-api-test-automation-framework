"""Negative scenarios — malformed, unauthorized and unsupported requests."""

from __future__ import annotations

import requests

import pytest

from qa_framework.api_client import ApiClient
from qa_framework.assertions import assert_error_body, assert_status
from qa_framework.settings import settings

pytestmark = [pytest.mark.negative, pytest.mark.regression]


def test_invalid_json_payload(base_url: str) -> None:
    response = requests.post(
        f"{base_url}/api/v1/tasks",
        data="{not-json",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {_token(base_url)}"},
        timeout=10,
    )
    assert_status(response, 422)


def _token(base_url: str) -> str:
    response = requests.post(
        f"{base_url}/api/v1/auth/token",
        json={"username": settings.username, "password": settings.password},
        timeout=10,
    )
    return str(response.json()["access_token"])


def test_missing_required_field(auth_client: ApiClient) -> None:
    assert_status(auth_client.post("/api/v1/tasks", json_body={"description": "no title"}), 422)


def test_incorrect_data_type(auth_client: ApiClient) -> None:
    assert_status(auth_client.post("/api/v1/tasks", json_body={"title": 12345}), 422)


def test_invalid_status_value(auth_client: ApiClient) -> None:
    assert_status(
        auth_client.post("/api/v1/tasks", json_body={"title": "x", "status": "unknown"}), 422
    )


def test_invalid_identifier(auth_client: ApiClient) -> None:
    assert_status(auth_client.get("/api/v1/tasks/not-an-integer"), 422)


def test_unauthorized_create(unauth_client: ApiClient) -> None:
    response = unauth_client.post("/api/v1/tasks", json_body={"title": "x"})
    assert_status(response, 401)
    assert_error_body(response, "missing_token")


def test_unsupported_method(auth_client: ApiClient) -> None:
    assert_status(auth_client.put("/api/v1/tasks", json_body={}), 405)


def test_invalid_pagination(auth_client: ApiClient) -> None:
    assert_status(auth_client.get("/api/v1/tasks", params={"page": 0}), 422)
    assert_status(auth_client.get("/api/v1/tasks", params={"page_size": 0}), 422)
    assert_status(auth_client.get("/api/v1/tasks", params={"page_size": 101}), 422)
