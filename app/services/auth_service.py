from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.schemas.auth_schema import TokenData
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.config import settings
from app.utils.hash import verify_password
from app.services.log_service import create_log


# ============================================================
# CREATE ACCESS TOKEN (Short lived)
# ============================================================
def create_access_token(data: dict) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {**data, "exp": expire, "iat": now}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


# ============================================================
# CREATE REFRESH TOKEN (Long lived)
# ============================================================
def create_refresh_token(db: Session, user_id: str) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {"sub": user_id, "exp": expire, "iat": now}
    token_str = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Save to DB (CORRECTED KEY NAMES)
    db_token = RefreshToken(
        user_id=user_id,
        token=token_str,        # ✔ CORRECT FIELD NAME
        expires_at=expire,
        revoked=False,
    )
    db.add(db_token)
    db.commit()

    return token_str


# ============================================================
# DECODE TOKEN
# ============================================================
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")

    except JWTError:
        raise HTTPException(401, "Invalid token")


# ============================================================
# AUTHENTICATE USER (Email + Password)
# ============================================================
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email.lower().strip()).first()

    if not user or not verify_password(password, user.password):
        create_log(db, None, f"Login failed: {email}")
        return None

    create_log(db, user.id, "Login successful")
    return user


# ============================================================
# LOGIN → returns access + refresh
# ============================================================
def login(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(401, "Incorrect email or password")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(db, str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "role": user.role,
    }


# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================
def refresh_access_token(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)
    user_id = payload.get("sub")

    # Validate DB entry (✔ FIXED FIELD NAME)
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if not db_token:
        raise HTTPException(401, "Refresh token invalid")

    if db_token.revoked:
        raise HTTPException(401, "Refresh token revoked")

    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(401, "Refresh token expired")

    # ROTATE TOKEN — delete old one
    db.delete(db_token)
    db.commit()

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token(db, user_id)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "user_id": user_id,
    }


# ============================================================
# LOGOUT → delete refresh token
# ============================================================
def logout(db: Session, refresh_token: str):
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)  # ✔ FIXED FIELD
        .first()
    )

    if db_token:
        db.delete(db_token)
        db.commit()

    return {"message": "Logged out successfully"}
