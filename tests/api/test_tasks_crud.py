"""CRUD, ownership and persistence scenarios over real HTTP."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from typing import Any

import pytest

from qa_framework.api_client import ApiClient
from qa_framework.assertions import assert_fields, assert_status

pytestmark = [pytest.mark.regression, pytest.mark.integration]


@pytest.mark.smoke
def test_create_task(task_factory: Callable[..., dict[str, Any]]) -> None:
    created = task_factory(title="Create me")
    assert_fields(
        created, {"id", "title", "description", "status", "owner", "created_at", "updated_at"}
    )
    assert created["title"] == "Create me"
    assert created["status"] == "pending"


def test_read_task(auth_client: ApiClient, task_factory: Callable[..., dict[str, Any]]) -> None:
    created = task_factory()
    response = auth_client.get(f"/api/v1/tasks/{created['id']}")
    assert_status(response, 200)
    assert response.json() == created


@pytest.mark.smoke
def test_list_tasks_with_pagination(
    auth_client: ApiClient, task_factory: Callable[..., dict[str, Any]]
) -> None:
    task_factory(title="First")
    task_factory(title="Second")
    response = auth_client.get("/api/v1/tasks", params={"page": 1, "page_size": 1})
    assert_status(response, 200)
    body = response.json()
    assert_fields(body, {"items", "total", "page", "page_size"})
    assert len(body["items"]) == 1 and body["page"] == 1 and body["page_size"] == 1
    assert body["total"] >= 2


def test_update_task(auth_client: ApiClient, task_factory: Callable[..., dict[str, Any]]) -> None:
    created = task_factory()
    response = auth_client.patch(
        f"/api/v1/tasks/{created['id']}",
        json_body={"title": "Renamed", "status": "completed"},
    )
    assert_status(response, 200)
    updated = response.json()
    assert updated["title"] == "Renamed" and updated["status"] == "completed"
    assert updated["updated_at"] >= created["updated_at"]


def test_delete_task(auth_client: ApiClient, task_factory: Callable[..., dict[str, Any]]) -> None:
    created = task_factory()
    assert_status(auth_client.delete(f"/api/v1/tasks/{created['id']}"), 204)
    assert_status(auth_client.get(f"/api/v1/tasks/{created['id']}"), 404)


def test_get_nonexistent_task(auth_client: ApiClient) -> None:
    assert_status(auth_client.get("/api/v1/tasks/99999999"), 404)


def test_update_nonexistent_task(auth_client: ApiClient) -> None:
    assert_status(auth_client.patch("/api/v1/tasks/99999999", json_body={"title": "x"}), 404)


def test_delete_nonexistent_task(auth_client: ApiClient) -> None:
    assert_status(auth_client.delete("/api/v1/tasks/99999999"), 404)


def test_database_persistence(
    task_factory: Callable[..., dict[str, Any]], db_connection: sqlite3.Connection
) -> None:
    created = task_factory(title="Persisted")
    row = db_connection.execute(
        "SELECT title, owner FROM tasks WHERE id = ?", (created["id"],)
    ).fetchone()
    assert row is not None and row["title"] == "Persisted"
    assert row["owner"] == created["owner"]


def test_other_user_task_forbidden(
    second_client: ApiClient, task_factory: Callable[..., dict[str, Any]]
) -> None:
    created = task_factory()
    assert_status(second_client.get(f"/api/v1/tasks/{created['id']}"), 403)


def test_list_only_own_tasks(
    second_client: ApiClient, task_factory: Callable[..., dict[str, Any]]
) -> None:
    task_factory(title="Owner only")
    body = second_client.get("/api/v1/tasks").json()
    from qa_framework.settings import settings

    assert all(item["owner"] == settings.second_username for item in body["items"])
    assert all(item["title"] != "Owner only" for item in body["items"])
