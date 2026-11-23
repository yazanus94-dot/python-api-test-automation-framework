"""Environment-driven configuration.

Values are read on each access so a test fixture can point the SUT at an
isolated database after the module has been imported. No secret is ever printed.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


class Settings:
    @property
    def app_name(self) -> str:
        return os.getenv("APP_NAME", "Task Management API")

    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", "data/tasks.db")

    @property
    def database_path(self) -> Path:
        return Path(self.database_url)

    @property
    def jwt_secret_key(self) -> str:
        return os.getenv("JWT_SECRET_KEY", "local-dev-secret-change-me")

    @property
    def jwt_algorithm(self) -> str:
        return os.getenv("JWT_ALGORITHM", "HS256")

    @property
    def access_token_expire_minutes(self) -> int:
        return _int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

    @property
    def test_username(self) -> str:
        return os.getenv("TEST_USERNAME", "qa_user")

    @property
    def test_password(self) -> str:
        return os.getenv("TEST_PASSWORD", "TestPassw0rd!")

    @property
    def second_username(self) -> str:
        return os.getenv("SECOND_USERNAME", "second_user")

    @property
    def second_password(self) -> str:
        return os.getenv("SECOND_PASSWORD", "SecondPassw0rd!")


settings = Settings()
