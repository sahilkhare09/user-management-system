from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.department_schema import (DepartmentCreate,DepartmentRead,DepartmentUpdate)

from app.database.db import get_db
from app.services.department_service import (create_department,list_departments,get_department,update_department,delete_department)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentRead)
def create_department_api(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    allowed_roles = ["superadmin", "organisation_admin"]

    if current_user.role.lower() not in allowed_roles:
        raise HTTPException(
            403, "Only organisation admins or superadmin can create departments"
        )

    # Org admin can only create within their own organisation
    if current_user.role.lower() != "superadmin":
        if current_user.organisation_id != payload.organisation_id:
            raise HTTPException(
                403,
                "Organisation Admin can create departments only in their own organisation",
            )

    # Manager validation (if provided)
    if payload.manager_id:
        manager = db.query(User).filter(User.id == payload.manager_id).first()

        if not manager:
            raise HTTPException(404, "Manager user not found")

        if manager.organisation_id != payload.organisation_id:
            raise HTTPException(403, "Manager must belong to the same organisation")

    return create_department(
        db, payload.name, payload.organisation_id, payload.manager_id
    )


@router.get("/", response_model=list[DepartmentRead])
def list_departments_api(db: Session = Depends(get_db)):
    return list_departments(db)


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department_api(department_id: UUID, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(404, "Department not found")
    return department


@router.put("/{department_id}", response_model=DepartmentRead)
def update_department_api(
    department_id: UUID,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    allowed_roles = ["superadmin", "organisation_admin"]

    if current_user.role.lower() not in allowed_roles:
        raise HTTPException(
            403, "Only superadmin or organisation admin can update departments"
        )

    department = get_department(db, department_id)
    if not department:
        raise HTTPException(404, "Department not found")

    # Org admin restriction
    if current_user.role.lower() != "superadmin":
        if current_user.organisation_id != department.organisation_id:
            raise HTTPException(
                403,
                "Organisation Admin cannot update a department of another organisation",
            )

    # Manager validation (if provided)
    if payload.manager_id:
        manager = db.query(User).filter(User.id == payload.manager_id).first()
        if not manager:
            raise HTTPException(404, "Manager user not found")
        if manager.organisation_id != department.organisation_id:
            raise HTTPException(403, "Manager must belong to the same organisation")

    return update_department(db, department_id, payload.name, payload.manager_id)


@router.delete("/{department_id}")
def delete_department_api(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    allowed_roles = ["superadmin", "organisation_admin"]

    if current_user.role.lower() not in allowed_roles:
        raise HTTPException(
            403, "Only superadmin or organisation admin can delete departments"
        )

    department = get_department(db, department_id)
    if not department:
        raise HTTPException(404, "Department not found")


    if current_user.role.lower() != "superadmin":
        if current_user.organisation_id != department.organisation_id:
            raise HTTPException(
                403, "You cannot delete a department of another organisation"
            )

    return delete_department(db, department_id)



@router.put("/{department_id}/assign-manager/{user_id}", response_model=DepartmentRead)
def assign_manager(
    department_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    allowed_roles = ["superadmin", "organisation_admin"]
    if current_user.role.lower() not in allowed_roles:
        raise HTTPException(
            403, "Only superadmin or organisation admin can assign managers"
        )

    department = get_department(db, department_id)
    if not department:
        raise HTTPException(404, "Department not found")

    if current_user.role.lower() != "superadmin":
        if current_user.organisation_id != department.organisation_id:
            raise HTTPException(
                403, "You cannot modify another organisation's department"
            )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.organisation_id != department.organisation_id:
        raise HTTPException(403, "Manager must belong to the same organisation")


    user.role = "department_manager"
    user.department_id = department_id

    department.manager_id = user_id

    db.commit()
    db.refresh(department)
    return department



@router.put("/{department_id}/remove-manager", response_model=DepartmentRead)
def remove_manager(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    allowed_roles = ["superadmin", "organisation_admin"]
    if current_user.role.lower() not in allowed_roles:
        raise HTTPException(
            403, "Only superadmin or organisation admin can remove managers"
        )

    department = get_department(db, department_id)
    if not department:
        raise HTTPException(404, "Department not found")

    # Org admin restriction
    if current_user.role.lower() != "superadmin":
        if current_user.organisation_id != department.organisation_id:
            raise HTTPException(
                403, "You cannot modify another organisation's department"
            )

    if department.manager_id:
        manager = db.query(User).filter(User.id == department.manager_id).first()
        if manager:
            manager.role = "employee"

    department.manager_id = None

    db.commit()
    db.refresh(department)
    return department
