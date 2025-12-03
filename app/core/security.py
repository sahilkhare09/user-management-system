from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=True)

# Standard authentication error
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired authentication token",
    headers={"WWW-Authenticate": "Bearer"},
)


# ============================================================
# TOKEN DECODER WITH PROPER VALIDATION
# ============================================================
def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
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


# ============================================================
# GET CURRENT USER (AUTH REQUIRED)
# ============================================================
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = creds.credentials
    user_id = decode_token(token)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    # Normalize role for all RBAC checks
    user.role = (user.role or "").lower()

    return user


# ============================================================
# RBAC HELPERS
# ============================================================


# ✔ SUPERADMIN ONLY
def require_superadmin(current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(403, "Superadmin access required")
    return current_user


# ✔ ORG ADMIN or SUPERADMIN
def require_org_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["organisation_admin", "superadmin"]:
        raise HTTPException(
            status_code=403,
            detail="Only organisation admins or superadmins can access this resource.",
        )
    return current_user


# ✔ FLEXIBLE ROLE CHECKER
def require_role(roles: list):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in [r.lower() for r in roles]:
            raise HTTPException(
                status_code=403, detail=f"Access denied — requires roles: {roles}"
            )
        return current_user

    return checker
