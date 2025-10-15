from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import create_or_get_user_by_phone, create_access_token, create_refresh_token
from app.models import UserRole

router = APIRouter()


class LoginRequest(BaseModel):
    phone_number: str
    user_type: UserRole = Field(default=UserRole.CUSTOMER)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = create_or_get_user_by_phone(db, payload.phone_number)
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
    return {
        "user_id": user.id,
        "active_role": payload.user_type.value,
        "roles": user.roles,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


