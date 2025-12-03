from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.schemas.auth_schema import TokenData
from app.models.user import User
from app.core.config import settings
from app.utils.hash import verify_password
from app.services.log_service import create_log


# -----------------------------------------------------------
# GENERATE JWT ACCESS TOKEN
# -----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# -----------------------------------------------------------
# VERIFY USER CREDENTIALS
# -----------------------------------------------------------
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email.lower().strip()).first()

    if not user:
        create_log(db, None, f"Login failed: {email}")
        return None

    if not verify_password(password, user.password):
        create_log(db, None, f"Login failed: {email}")
        return None

    create_log(db, user.id, "Login successful")
    return user


# -----------------------------------------------------------
# LOGIN FUNCTION (USED BY auth_router)
# -----------------------------------------------------------
def login(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "role": user.role,
    }
