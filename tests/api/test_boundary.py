"""Boundary scenarios for field lengths and pagination limits."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from qa_framework.api_client import ApiClient
from qa_framework.assertions import assert_status

pytestmark = [pytest.mark.negative, pytest.mark.regression]


def test_minimum_title_length(task_factory: Callable[..., dict[str, Any]]) -> None:
    assert task_factory(title="A")["title"] == "A"


def test_below_minimum_title_length(auth_client: ApiClient) -> None:
    assert_status(auth_client.post("/api/v1/tasks", json_body={"title": ""}), 422)


def test_blank_title_rejected(auth_client: ApiClient) -> None:
    assert_status(auth_client.post("/api/v1/tasks", json_body={"title": "   "}), 422)


def test_maximum_title_length(task_factory: Callable[..., dict[str, Any]]) -> None:
    created = task_factory(title="T" * 200)
    assert len(created["title"]) == 200


def test_above_maximum_title_length(auth_client: ApiClient) -> None:
    assert_status(auth_client.post("/api/v1/tasks", json_body={"title": "T" * 201}), 422)


def test_maximum_description_length(task_factory: Callable[..., dict[str, Any]]) -> None:
    created = task_factory(description="D" * 1000)
    assert len(created["description"]) == 1000


def test_above_maximum_description_length(auth_client: ApiClient) -> None:
    assert_status(
        auth_client.post("/api/v1/tasks", json_body={"title": "x", "description": "D" * 1001}), 422
    )


def test_pagination_upper_bound(auth_client: ApiClient) -> None:
    response = auth_client.get("/api/v1/tasks", params={"page": 1, "page_size": 100})
    assert_status(response, 200)
    assert response.json()["page_size"] == 100
