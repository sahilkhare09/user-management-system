from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.database.db import get_db
from app.services.auth_service import (login as login_service,refresh_access_token,logout)

from app.core.security import get_current_user
from app.models.user import User


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return login_service(db, form_data.username, form_data.password)



@router.post("/refresh")
def refresh_token(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Accepts:
    {
        "refresh_token": "your_refresh_token"
    }
    """
    return refresh_access_token(db, payload.refresh_token)



@router.post("/logout")
def logout_user(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Accepts:
    {
        "refresh_token": "your_refresh_token"
    }
    """
    return logout(db, payload.refresh_token)



@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
    }



@router.put("/make-admin/{user_id}")
def make_admin(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "superadmin":
        raise HTTPException(403, "Only superadmin can promote users to admin.")

    if current_user.id == user_id:
        raise HTTPException(400, "You cannot promote yourself.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.role in ["admin", "superadmin"]:
        raise HTTPException(400, f"User already has role: {user.role}")

    user.role = "admin"
    db.commit()

    return {"message": f"{user.email} is now an admin"}



@router.put("/make-org-admin/{user_id}")
def make_organisation_admin(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "superadmin":
        raise HTTPException(403, "Only superadmin can promote to organisation admin.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.role = "organisation_admin"
    db.commit()

    return {"message": f"{user.email} is now organisation admin"}
