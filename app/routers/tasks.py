"""Authenticated task CRUD with pagination and ownership checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..database import connection
from ..models import task_from_row
from ..schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from ..security import decode_access_token

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def required_error(code: int, message: str, reason: str) -> HTTPException:
    return HTTPException(
        status_code=code,
        detail={"detail": message, "code": reason},
        headers={"WWW-Authenticate": "Bearer"} if code == 401 else None,
    )


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> str:
    if credentials is None or not credentials.credentials:
        raise required_error(401, "Missing or malformed Authorization header", "missing_token")
    try:
        return decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise required_error(401, "Invalid or expired token", "invalid_token") from exc


CurrentUser = Annotated[str, Depends(get_current_user)]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("", response_model=TaskListResponse)
def list_tasks(
    user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TaskListResponse:
    with connection() as conn:
        total = int(
            conn.execute("SELECT COUNT(*) AS n FROM tasks WHERE owner = ?", (user,)).fetchone()["n"]
        )
        rows = conn.execute(
            "SELECT * FROM tasks WHERE owner = ? ORDER BY id LIMIT ? OFFSET ?",
            (user, page_size, (page - 1) * page_size),
        ).fetchall()
    return TaskListResponse(
        items=[task_from_row(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, user: CurrentUser) -> TaskResponse:
    timestamp = _now()
    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, status, owner, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (payload.title, payload.description, payload.status, user, timestamp, timestamp),
        )
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return task_from_row(row)


def _owned_row(task_id: int, user: str):
    with connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise required_error(404, "Task not found", "not_found")
    if str(row["owner"]) != user:
        raise required_error(403, "Task belongs to another user", "forbidden")
    return row


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, user: CurrentUser) -> TaskResponse:
    return task_from_row(_owned_row(task_id, user))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, user: CurrentUser) -> TaskResponse:
    _owned_row(task_id, user)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise required_error(422, "No updatable fields supplied", "empty_update")
    assignments = ", ".join(f"{field} = ?" for field in changes)
    values = list(changes.values()) + [_now(), task_id]
    with connection() as conn:
        conn.execute(f"UPDATE tasks SET {assignments}, updated_at = ? WHERE id = ?", values)
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return task_from_row(row)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_task(task_id: int, user: CurrentUser) -> Response:
    _owned_row(task_id, user)
    with connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
