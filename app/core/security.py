from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.user import User
from app.core.config import settings


bearer_scheme = HTTPBearer(auto_error=True)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired authentication token",
    headers={"WWW-Authenticate": "Bearer"},
)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception

        return user_id

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError:
        raise credentials_exception



def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    raw_token = token.credentials  # Extract "Bearer <token>"

    # Decode → get user_id
    user_id_str = decode_token(raw_token)

    try:
        user_id = UUID(user_id_str)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_superadmin(current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(403, "Superadmin access required")
    return current_user


def require_org_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["organisation_admin", "superadmin"]:
        raise HTTPException(
            status_code=403,
            detail="Only organisation admins or superadmins allowed",
        )
    return current_user


def require_role(roles: list):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role.lower() not in [r.lower() for r in roles]:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied — requires roles: {roles}",
            )
        return current_user

    return checker
