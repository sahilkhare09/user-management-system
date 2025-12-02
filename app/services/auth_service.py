# app/services/auth_service.py

from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.auth_schema import TokenData
from app.models.user import User
from app.core.config import settings
from app.utils.hash import verify_password
from app.services.log_service import create_log


# ============================================================
# CREATE ACCESS TOKEN
# ============================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()

    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({
        "exp": expire,
        "iat": now,
        "sub": data.get("sub")  # ensure subject always present
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# ============================================================
# AUTHENTICATE USER
# ============================================================
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email.lower().strip()).first()

    if not user:
        create_log(db, None, f"Login failed (email not found): {email}")
        return None

    if not verify_password(password, user.password):
        create_log(db, user.id, "Login failed (wrong password)")
        return None

    create_log(db, user.id, "Login successful")
    return user


# ============================================================
# VERIFY JWT TOKEN (USED BY get_current_user)
# ============================================================
def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(sub=user_id)

    except ExpiredSignatureError:
        raise HTTPException(
            401,
            "Token expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError:
        raise HTTPException(
            401,
            "Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
# LOGIN (USED BY auth_router)
# ============================================================
def login(db: Session, email: str, password: str):
    email = email.lower().strip()

    user = authenticate_user(db, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token_data = {"sub": str(user.id)}

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "role": user.role.lower()
    }
