"""Test configuration loaded from environment / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class TestSettings:
    base_url: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8765")
    database_url: str = os.getenv("DATABASE_URL", "data/tasks.db")
    username: str = os.getenv("TEST_USERNAME", "qa_user")
    password: str = os.getenv("TEST_PASSWORD", "TestPassw0rd!")
    second_username: str = os.getenv("SECOND_USERNAME", "second_user")
    second_password: str = os.getenv("SECOND_PASSWORD", "SecondPassw0rd!")
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "10"))


settings = TestSettings()
