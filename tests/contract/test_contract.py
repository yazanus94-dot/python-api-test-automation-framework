"""Response/request contract validation using OpenAPI JSON Schemas."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from qa_framework.api_client import ApiClient
from qa_framework.assertions import assert_json_content_type, assert_status, validate_schema

pytestmark = [pytest.mark.contract, pytest.mark.regression]


@pytest.fixture(scope="module")
def schemas(base_url: str) -> dict[str, dict]:
    document = ApiClient(base_url).get("/openapi.json").json()
    return document["components"]["schemas"]


def test_create_response_matches_schema(
    task_factory: Callable[..., dict[str, Any]], schemas: dict[str, dict]
) -> None:
    created = task_factory()
    validate_schema(created, schemas["TaskResponse"])


def test_list_response_matches_schema(auth_client: ApiClient, schemas: dict[str, dict]) -> None:
    response = auth_client.get("/api/v1/tasks")
    assert_status(response, 200)
    validate_schema(response.json(), schemas["TaskListResponse"])


def test_status_code_contract(
    auth_client: ApiClient, task_factory: Callable[..., dict[str, Any]]
) -> None:
    created = task_factory()
    assert_status(auth_client.get(f"/api/v1/tasks/{created['id']}"), 200)
    assert_status(
        auth_client.patch(f"/api/v1/tasks/{created['id']}", json_body={"status": "completed"}), 200
    )
    assert_status(auth_client.delete(f"/api/v1/tasks/{created['id']}"), 204)


def test_json_content_type_contract(auth_client: ApiClient) -> None:
    for path in ("/health", "/api/v1/tasks", "/openapi.json"):
        response = auth_client.get(path)
        assert_status(response, 200)
        assert_json_content_type(response)


def test_request_validation_contract(auth_client: ApiClient) -> None:
    response = auth_client.post("/api/v1/tasks", json_body={"title": None})
    assert_status(response, 422)
    assert response.json()["code"] == "validation_error"


def test_task_create_schema_enforces_status_enum(schemas: dict[str, dict]) -> None:
    status_schema = schemas["TaskCreate"]["properties"]["status"]
    assert set(status_schema["enum"]) == {"pending", "in_progress", "completed"}
