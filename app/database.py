"""SQLite persistence with deterministic seeded users."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import settings
from .security import hash_password


@contextmanager
def connection():
    path: Path = settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                owner TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner) REFERENCES users(username)
            )
        """)
        for username, password in (
            (settings.test_username, settings.test_password),
            (settings.second_username, settings.second_password),
        ):
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password)),
            )


def get_password_hash(username: str) -> str | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
    return str(row["password_hash"]) if row else None
