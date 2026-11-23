"""OpenAPI document and endpoint-contract checks."""

from __future__ import annotations

import pytest

from qa_framework.api_client import ApiClient
from qa_framework.assertions import assert_fields, assert_json_content_type, assert_status

pytestmark = [pytest.mark.contract, pytest.mark.regression]

EXPECTED_PATHS = {
    "/health",
    "/api/v1/auth/token",
    "/api/v1/tasks",
    "/api/v1/tasks/{task_id}",
}


@pytest.fixture(scope="module")
def openapi_document(base_url: str) -> dict:
    client = ApiClient(base_url)
    response = client.get("/openapi.json")
    assert_status(response, 200)
    assert_json_content_type(response)
    return response.json()


def test_openapi_version(openapi_document: dict) -> None:
    assert openapi_document["openapi"].startswith("3.")
    assert openapi_document["info"]["title"]


def test_all_expected_endpoints_declared(openapi_document: dict) -> None:
    assert EXPECTED_PATHS.issubset(set(openapi_document["paths"]))


def test_task_create_request_schema(openapi_document: dict) -> None:
    schema = openapi_document["components"]["schemas"]["TaskCreate"]
    assert "title" in schema["required"]
    assert schema["properties"]["title"]["maxLength"] == 200


def test_task_response_schema_fields(openapi_document: dict) -> None:
    schema = openapi_document["components"]["schemas"]["TaskResponse"]
    assert_fields(schema, {"properties"})
    assert {"id", "title", "status", "owner", "created_at"}.issubset(set(schema["required"]))


def test_health_content_type_and_fields(unauth_client: ApiClient) -> None:
    response = unauth_client.get("/health")
    assert_status(response, 200)
    assert_json_content_type(response)
    assert_fields(response.json(), {"status", "service"})


def test_error_contract_shape(unauth_client: ApiClient) -> None:
    response = unauth_client.get("/api/v1/tasks")
    assert_status(response, 401)
    assert_fields(response.json(), {"detail", "code"})


def test_bearer_security_scheme_declared(openapi_document: dict) -> None:
    schemes = openapi_document["components"].get("securitySchemes", {})
    assert any(str(scheme.get("scheme", "")).lower() == "bearer" for scheme in schemes.values())
