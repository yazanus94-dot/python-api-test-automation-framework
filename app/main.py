"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import settings
from .database import init_db
from .routers import auth, tasks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize the isolated database once when the SUT starts."""
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "code": "validation_error",
            "errors": [str(error.get("msg", "")) for error in exc.errors()],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Flatten structured details into a consistent ``{detail, code}`` envelope."""
    detail = exc.detail
    if isinstance(detail, dict):
        content = dict(detail)
    else:
        content = {"detail": str(detail), "code": "http_error"}
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers or None)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth.router)
app.include_router(tasks.router)
