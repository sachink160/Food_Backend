from datetime import datetime, timedelta
import random
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from app import models
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db
from app import models, database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_minutes: int, token_type: str, db: Session) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    jti = str(uuid4())

    # Add user_id from database if needed
    db_user = db.query(models.User).filter(models.User.username == data["sub"]).first()
    if db_user:
        to_encode.update({
            "exp": expire,
            "type": token_type,
            "jti": jti,
            "user_id": db_user.id
        })
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        db_token = models.OutstandingToken(
            jti=jti,
            user_id=db_user.id,
            token_type=token_type
        )
        db.add(db_token)
        db.commit()
        return token
    else:
        raise HTTPException(status_code=401, detail="User not found")


def create_access_token(data: dict, db: Session) -> str:
    return create_token(data, ACCESS_TOKEN_EXPIRE_MINUTES, "access", db)

def create_refresh_token(data: dict, db: Session) -> str:
    return create_token(data, 60 * 24 * 7, "refresh", db)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def is_blacklisted(jti: str, db: Session) -> bool:
    return db.query(models.BlacklistToken).filter(models.BlacklistToken.jti == jti).first() is not None

def blacklist_token(token: str, db: Session):
    payload = decode_token(token)
    if payload:
        jti = payload.get("jti")
        if jti:
            db.add(models.BlacklistToken(jti=jti))
            db.commit()

def get_token_type(token: str) -> str | None:
    payload = decode_token(token)
    return payload.get("type") if payload else None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(database.get_db)
) -> models.User:
    token = credentials.credentials  # Extract token from header
    payload = decode_token(token)
    user_id = payload.get("user_id") if payload else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# OTP utilities
def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"

def send_otp_sms(phone_number: str, code: str):
    # Integrate with real SMS provider later (Twilio, etc.)
    # For now, we just log the OTP
    print(f"OTP for {phone_number}: {code}")


def create_or_get_user_by_phone(db: Session, phone_number: str) -> models.User:
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    if user:
        return user
    # Create a minimal user; username/email placeholders derived from phone
    username = f"user_{phone_number}"
    email = f"{phone_number}@example.com"
    user = models.User(
        email=email,
        username=username,
        hashed_password=pwd_context.hash(generate_otp()),
        full_name=phone_number,
        phone_number=phone_number,
        is_verified=True,
        roles=[models.UserRole.CUSTOMER.value]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_and_store_otp(db: Session, phone_number: str) -> str:
    code = generate_otp()
    expires = datetime.utcnow() + timedelta(minutes=5)
    otp = models.OTPCode(phone_number=phone_number, code=code, expires_at=expires)
    db.add(otp)
    db.commit()
    send_otp_sms(phone_number, code)
    return code


def verify_otp_and_issue_tokens(db: Session, phone_number: str, code: str):
    otp = (
        db.query(models.OTPCode)
        .filter(models.OTPCode.phone_number == phone_number, models.OTPCode.code == code, models.OTPCode.consumed == False)
        .order_by(models.OTPCode.created_at.desc())
        .first()
    )
    if not otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    otp.consumed = True
    db.commit()

    user = create_or_get_user_by_phone(db, phone_number)

    subject = user.username
    access_token = create_access_token({"sub": subject}, db)
    refresh_token = create_refresh_token({"sub": subject}, db)
    return user, access_token, refresh_token
