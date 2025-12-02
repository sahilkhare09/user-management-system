from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.auth_schema import Token
from app.services.auth_service import authenticate_user, create_access_token
from app.services.log_service import create_log
from app.database.db import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.department import Department

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


# -------------------------------------------------------
# LOGIN
# -------------------------------------------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    # log login event
    create_log(db, user.id, f"User logged in: {user.email}")

    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------------------------------------
# /me → currently logged-in user
# -------------------------------------------------------
@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


# -------------------------------------------------------
# MAKE ADMIN (SUPERADMIN ONLY)
# -------------------------------------------------------
@router.put("/make-admin/{user_id}")
def make_admin(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    db.refresh(user)

    create_log(db, current_user.id, f"Promoted {user.email} to admin")

    return {"message": f"{user.email} is now an admin"}


# -------------------------------------------------------
# MAKE ORG ADMIN (SUPERADMIN ONLY)
# -------------------------------------------------------
@router.put("/make-org-admin/{user_id}")
def make_organisation_admin(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "superadmin":
        raise HTTPException(403, "Only superadmin can promote to organisation admin.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.role == "organisation_admin":
        raise HTTPException(400, "User is already an organisation admin")

    user.role = "organisation_admin"
    db.commit()
    db.refresh(user)

    create_log(db, current_user.id, f"Promoted {user.email} to organisation admin")

    return {"message": f"{user.email} promoted to organisation admin"}


# -------------------------------------------------------
# MAKE DEPARTMENT MANAGER
# superadmin → allowed everywhere
# org-admin → only inside own organisation
# -------------------------------------------------------
@router.put("/make-department-manager/{user_id}/{department_id}")
def make_department_manager(
    user_id: UUID,
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in ["superadmin", "organisation_admin"]:
        raise HTTPException(403, "Not allowed")

    # Fetch department
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(404, "Department not found")

    # ORG ADMIN restriction → must control only their organisation
    if current_user.role == "organisation_admin":
        if current_user.organisation_id != department.organisation_id:
            raise HTTPException(
                403,
                "Organisation admin can assign manager only inside their own organisation"
            )

    # Fetch user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # manager must belong to same organisation
    if user.organisation_id != department.organisation_id:
        raise HTTPException(400, "User must belong to the same organisation as the department")

    # assign role
    user.role = "department_manager"
    department.manager_id = user.id

    db.commit()
    db.refresh(user)
    db.refresh(department)

    create_log(db, current_user.id, f"Made {user.email} manager of {department.name}")

    return {
        "message": f"{user.email} is now manager of {department.name}",
        "department_id": str(department.id),
        "manager_id": str(user.id)
    }





