"""Database row mapping helpers."""

from __future__ import annotations

import sqlite3

from .schemas import TaskResponse


def task_from_row(row: sqlite3.Row) -> TaskResponse:
    return TaskResponse(
        id=int(row["id"]),
        title=str(row["title"]),
        description=str(row["description"]),
        status=str(row["status"]),  # type: ignore[arg-type]
        owner=str(row["owner"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
