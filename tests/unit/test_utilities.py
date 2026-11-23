"""Unit checks for framework utilities (no HTTP)."""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.security import create_access_token, decode_access_token, hash_password, verify_password
from qa_framework.helpers import redact, unique_payload

pytestmark = [pytest.mark.unit, pytest.mark.regression]


def test_password_hash_roundtrip() -> None:
    encoded = hash_password("CorrectHorse9!")
    assert verify_password("CorrectHorse9!", encoded)
    assert not verify_password("wrong", encoded)


def test_token_roundtrip_and_expiry() -> None:
    token = create_access_token("qa_user")
    assert decode_access_token(token) == "qa_user"
    expired = create_access_token("qa_user", expires_delta=timedelta(seconds=-5))
    with pytest.raises(ValueError):
        decode_access_token(expired)


def test_redaction_hides_credentials() -> None:
    payload = {
        "password": "secret",
        "access_token": "abc",
        "nested": [{"Authorization": "Bearer xyz"}],
    }
    cleaned = redact(payload)
    assert "secret" not in str(cleaned)
    assert "abc" not in str(cleaned)
    assert "xyz" not in str(cleaned)


def test_unique_payload_is_independent() -> None:
    first = unique_payload("a")
    second = unique_payload("a")
    assert first != second
    assert set(first) == {"title", "description", "status"}
