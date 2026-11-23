"""JWT token issuance."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..config import settings
from ..database import get_password_hash
from ..schemas import TokenRequest, TokenResponse
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def unauthorized(detail: str = "Invalid username or password") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"detail": detail, "code": "invalid_credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/token", response_model=TokenResponse)
def issue_token(payload: TokenRequest) -> TokenResponse:
    stored_hash = get_password_hash(payload.username)
    if stored_hash is None or not verify_password(payload.password, stored_hash):
        raise unauthorized()
    token = create_access_token(payload.username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )
