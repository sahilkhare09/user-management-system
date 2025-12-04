from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.models.user import User
from app.models.department import Department
from app.models.organisation import Organisation
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.core.security import get_current_user
from app.utils.hash import hash_password
from app.services.log_service import create_log

router = APIRouter(prefix="/api/v1/users", tags=["Users"])



def normalize_role(role: str):
    return role.lower().strip() if role else role


def require_role(user: User, allowed: list[str]):
    if normalize_role(user.role) not in allowed:
        raise HTTPException(403, f"Allowed roles: {allowed}")


def ensure_same_org(current_user: User, org_id: UUID):
    if current_user.organisation_id != org_id:
        raise HTTPException(403, "Not allowed — different organisation")


def ensure_same_department(current_user: User, dept_id: UUID):
    if current_user.department_id != dept_id:
        raise HTTPException(403, "Not allowed — different department")


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # First user → SUPERADMIN
    if db.query(User).count() == 0:
        assigned_role = "superadmin"

    else:
        current_role = normalize_role(current_user.role)
        requested_role = normalize_role(payload.role)

        if current_role == "superadmin":
            assigned_role = requested_role or "employee"

        elif current_role == "organisation_admin":
            if requested_role in ["superadmin", "organisation_admin"]:
                raise HTTPException(403, "Org Admin cannot create admin roles")

            if payload.organisation_id != current_user.organisation_id:
                raise HTTPException(403, "Org Admin can create only in their org")

            assigned_role = requested_role or "employee"

        else:
            raise HTTPException(403, "Only admins can create users")

    # Validate organisation
    if payload.organisation_id:
        org = (
            db.query(Organisation)
            .filter(Organisation.id == payload.organisation_id)
            .first()
        )
        if not org:
            raise HTTPException(404, "Organisation not found")

    # Validate department
    if payload.department_id:
        dept = (
            db.query(Department).filter(Department.id == payload.department_id).first()
        )
        if not dept:
            raise HTTPException(404, "Department not found")

        if dept.organisation_id != payload.organisation_id:
            raise HTTPException(403, "Department does not belong to this organisation")

    # Duplicate email check
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    new_user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        age=payload.age,
        email=payload.email,
        password=hash_password(payload.password),
        role=assigned_role,
        organisation_id=payload.organisation_id,
        department_id=payload.department_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_log(db, current_user.id, f"Created user {new_user.email}")

    return new_user


@router.get("", response_model=list[UserRead])
def get_all_users(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = normalize_role(current_user.role)

    q = db.query(User)

    if role == "superadmin":
        pass  # superadmin sees everything
    elif role == "organisation_admin":
        q = q.filter(User.organisation_id == current_user.organisation_id)
    elif role == "department_manager":
        q = q.filter(User.department_id == current_user.department_id)
    else:
        return [current_user]

    return q.offset((page - 1) * limit).limit(limit).all()



@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    role = normalize_role(current_user.role)

    if role == "superadmin":
        return user

    if role == "organisation_admin":
        ensure_same_org(current_user, user.organisation_id)
        return user

    if role == "department_manager":
        ensure_same_department(current_user, user.department_id)
        return user

    if current_user.id == user_id:
        return user

    raise HTTPException(403, "Not allowed")


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    role = normalize_role(current_user.role)

    # Superadmin → full access
    if role == "superadmin":
        pass

    elif role == "organisation_admin":
        ensure_same_org(current_user, user.organisation_id)

    elif role == "department_manager":
        ensure_same_department(current_user, user.department_id)

        forbidden_fields = ["role", "organisation_id", "department_id"]
        if any(getattr(payload, f) for f in forbidden_fields):
            raise HTTPException(
                403, "Department Manager cannot modify role/org/department"
            )

    elif current_user.id == user_id:
        forbidden_fields = ["role", "organisation_id", "department_id"]
        if any(getattr(payload, f) for f in forbidden_fields):
            raise HTTPException(403, "Employees cannot modify role/org/department")

    else:
        raise HTTPException(403, "Not allowed")

    # Duplicate email check
    if payload.email:
        exists = (
            db.query(User)
            .filter(User.email == payload.email, User.id != user_id)
            .first()
        )
        if exists:
            raise HTTPException(400, "Email already used by another user")

    data = payload.dict(exclude_unset=True)

    if "password" in data:
        data["password"] = hash_password(data["password"])

    # Validate department update
    if data.get("department_id"):
        dept = (
            db.query(Department).filter(Department.id == data["department_id"]).first()
        )
        if not dept:
            raise HTTPException(404, "Department not found")

        if (
            data.get("organisation_id")
            and dept.organisation_id != data["organisation_id"]
        ):
            raise HTTPException(403, "Department does not belong to this organisation")

    # Apply update
    for k, v in data.items():
        setattr(user, k, v)

    db.commit()
    db.refresh(user)

    create_log(db, current_user.id, f"Updated user {user.email}")

    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    role = normalize_role(current_user.role)

    if role == "superadmin":
        pass
    elif role == "organisation_admin":
        ensure_same_org(current_user, user.organisation_id)
    else:
        raise HTTPException(403, "Permission denied")

    db.delete(user)
    db.commit()

    create_log(db, current_user.id, f"Deleted user {user.email}")

    return {"message": "User deleted successfully"}

