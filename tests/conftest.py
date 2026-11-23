"""Live-server fixtures: all API tests use real HTTP against a local Uvicorn SUT."""

from __future__ import annotations

import os
import sqlite3
import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
import uvicorn

from qa_framework.api_client import ApiClient
from qa_framework.helpers import unique_payload, wait_for_health
from qa_framework.settings import settings

PORT = int(os.getenv("TEST_PORT", "8765"))
BASE_URL = os.getenv("API_BASE_URL", f"http://127.0.0.1:{PORT}")
Path("reports").mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def database_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("sut_database") / "tasks.db"


@pytest.fixture(scope="session", autouse=True)
def live_server(database_path: Path) -> Iterator[str]:
    """Start the real FastAPI app, or target an external API when configured."""
    if os.getenv("USE_EXTERNAL_API") == "1":
        wait_for_health(BASE_URL)
        yield BASE_URL
        return

    os.environ["DATABASE_URL"] = str(database_path)
    os.environ["JWT_SECRET_KEY"] = "automation-test-secret-not-for-production"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

    from app.main import app

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        wait_for_health(BASE_URL)
    except RuntimeError:
        server.should_exit = True
        thread.join(timeout=5)
        raise
    yield BASE_URL
    server.should_exit = True
    thread.join(timeout=10)


@pytest.fixture(scope="session")
def base_url(live_server: str) -> str:
    return live_server


@pytest.fixture
def unauth_client(base_url: str) -> ApiClient:
    return ApiClient(base_url)


def _login(base_url: str, username: str, password: str) -> str:
    response = requests.post(
        f"{base_url}/api/v1/auth/token",
        json={"username": username, "password": password},
        timeout=10,
    )
    assert response.status_code == 200, response.text
    return str(response.json()["access_token"])


@pytest.fixture(scope="session")
def auth_token(base_url: str) -> str:
    return _login(base_url, settings.username, settings.password)


@pytest.fixture(scope="session")
def second_token(base_url: str) -> str:
    return _login(base_url, settings.second_username, settings.second_password)


@pytest.fixture
def auth_client(base_url: str, auth_token: str) -> ApiClient:
    client = ApiClient(base_url)
    client.set_token(auth_token)
    return client


@pytest.fixture
def second_client(base_url: str, second_token: str) -> ApiClient:
    client = ApiClient(base_url)
    client.set_token(second_token)
    return client


@pytest.fixture
def task_factory(auth_client: ApiClient) -> Iterator[Callable[..., dict[str, Any]]]:
    """Create tasks through HTTP and delete them after the test."""
    created: list[int] = []

    def create(**overrides: Any) -> dict[str, Any]:
        payload = unique_payload()
        payload.update(overrides)
        response = auth_client.post("/api/v1/tasks", json_body=payload, expected_status=201)
        body = response.json()
        created.append(int(body["id"]))
        return body

    yield create
    for task_id in created:
        auth_client.delete(f"/api/v1/tasks/{task_id}")


@pytest.fixture
def db_connection(database_path: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(str(database_path))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
