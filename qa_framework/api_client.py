"""Reusable HTTP client for all verbs with redacted diagnostics."""

from __future__ import annotations

import json
from typing import Any

import requests

from .helpers import redact
from .logging_config import logger
from .settings import settings


class ApiClient:
    """Thin Session wrapper supporting GET/POST/PUT/PATCH/DELETE."""

    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self.session = requests.Session()
        self.token = token

    def set_token(self, token: str) -> None:
        self.token = token

    def clear_token(self) -> None:
        self.token = None

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        data: Any = None,
        params: dict[str, Any] | None = None,
        expected_status: int | None = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = self.session.request(
            method.upper(),
            url,
            json=json_body,
            data=data,
            params=params,
            headers=self.headers,
            timeout=settings.request_timeout,
        )
        logger.info(
            {
                "method": method.upper(),
                "url": url,
                "status": response.status_code,
                "request_body": redact(json_body if json_body is not None else data),
                "response_body": redact(self._safe_json(response)),
            }
        )
        if expected_status is not None and response.status_code != expected_status:
            raise AssertionError(
                f"Expected {expected_status} from {method.upper()} {path}, "
                f"got {response.status_code}: {response.text[:300]}"
            )
        return response

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except (ValueError, json.JSONDecodeError):
            return response.text[:300]

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
