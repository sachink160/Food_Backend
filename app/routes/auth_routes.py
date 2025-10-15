from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import (
    create_or_get_user_by_phone,
    create_access_token,
    create_refresh_token,
    blacklist_token,
    security,
)
from app.models import UserRole
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional

router = APIRouter()


class LoginRequest(BaseModel):
    phone_number: str
    user_type: UserRole = Field(default=UserRole.CUSTOMER)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = create_or_get_user_by_phone(db, payload.phone_number)
    # Backfill essential profile fields if missing
    updated = False
    if not getattr(user, "username", None):
        user.username = f"user_{user.phone_number or user.id}"
        updated = True
    if not getattr(user, "email", None):
        user.email = f"{user.phone_number or user.username}@example.com"
        updated = True
    if not getattr(user, "full_name", None):
        user.full_name = user.phone_number or user.username
        updated = True
    if not getattr(user, "roles", None) or len(user.roles) == 0:
        user.roles = [payload.user_type.value]
        updated = True
    if updated:
        db.add(user)
        db.commit()
        db.refresh(user)
    # ensure requested role exists for this user
    if payload.user_type.value not in (user.roles or []):
        roles = (user.roles or []) + [payload.user_type.value]
        user.roles = list(dict.fromkeys(roles))
        db.add(user)
        db.commit()
        db.refresh(user)
    subject = user.username
    token_claims = {"sub": subject, "role": payload.user_type.value}
    access_token = create_access_token(token_claims, db)
    refresh_token = create_refresh_token(token_claims, db)
    # Mark profile as incomplete if placeholder values are being used
    profile_incomplete = False
    if (
        (user.username or "").startswith("user_")
        or (user.email or "").endswith("@example.com")
        or (user.full_name or "") == (user.phone_number or "")
    ):
        profile_incomplete = True
    return {"success": True, "data": {
        "user_id": user.id,
        "active_role": payload.user_type.value,
        "roles": user.roles,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "profile_incomplete": profile_incomplete,
    }}


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


@router.post("/logout")
def logout(
    payload: LogoutRequest | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Blacklist the current access token
    access_token = credentials.credentials
    blacklist_token(access_token, db)

    # Optionally blacklist the refresh token if provided
    if payload and payload.refresh_token:
        blacklist_token(payload.refresh_token, db)

    return {"success": True, "data": {"message": "Logged out successfully"}}

