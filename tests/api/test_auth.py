"""Authentication scenarios — real HTTP requests."""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.security import create_access_token
from qa_framework.api_client import ApiClient
from qa_framework.assertions import (
    assert_error_body,
    assert_fields,
    assert_json_content_type,
    assert_status,
)
from qa_framework.settings import settings

pytestmark = pytest.mark.authentication


@pytest.mark.smoke
def test_valid_login_returns_bearer_token(unauth_client: ApiClient) -> None:
    response = unauth_client.post(
        "/api/v1/auth/token",
        json_body={"username": settings.username, "password": settings.password},
    )
    assert_status(response, 200)
    assert_json_content_type(response)
    assert_fields(response.json(), {"access_token", "token_type", "expires_in"})
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] > 0


@pytest.mark.regression
def test_invalid_username_rejected(unauth_client: ApiClient) -> None:
    response = unauth_client.post(
        "/api/v1/auth/token",
        json_body={"username": "no_such_user", "password": settings.password},
    )
    assert_status(response, 401)
    assert_error_body(response, "invalid_credentials")


@pytest.mark.regression
def test_invalid_password_rejected(unauth_client: ApiClient) -> None:
    response = unauth_client.post(
        "/api/v1/auth/token",
        json_body={"username": settings.username, "password": "wrong-password"},
    )
    assert_status(response, 401)
    assert_error_body(response, "invalid_credentials")


@pytest.mark.regression
def test_missing_credentials_rejected(unauth_client: ApiClient) -> None:
    response = unauth_client.post("/api/v1/auth/token", json_body={})
    assert_status(response, 422)
    assert_error_body(response, "validation_error")


@pytest.mark.regression
def test_invalid_token_rejected(base_url: str) -> None:
    client = ApiClient(base_url, token="not-a-jwt")
    assert_status(client.get("/api/v1/tasks"), 401)
    assert_error_body(client.get("/api/v1/tasks"), "invalid_token")


@pytest.mark.regression
def test_expired_token_rejected(base_url: str) -> None:
    expired = create_access_token(settings.username, expires_delta=timedelta(seconds=-10))
    client = ApiClient(base_url, token=expired)
    assert_status(client.get("/api/v1/tasks"), 401)
    assert_error_body(client.get("/api/v1/tasks"), "invalid_token")


@pytest.mark.regression
def test_missing_authorization_header_rejected(unauth_client: ApiClient) -> None:
    assert_status(unauth_client.get("/api/v1/tasks"), 401)
    assert_error_body(unauth_client.get("/api/v1/tasks"), "missing_token")


@pytest.mark.smoke
def test_valid_token_allows_protected_endpoint(auth_client: ApiClient) -> None:
    assert_status(auth_client.get("/api/v1/tasks"), 200)
