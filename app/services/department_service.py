from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.models.department import Department
from app.models.organisation import Organisation
from app.models.user import User


# -------------------------------------------------------
# CREATE DEPARTMENT
# -------------------------------------------------------
def create_department(db: Session, name: str, organisation_id: UUID, manager_id: UUID | None):

    # Check if organisation exists
    org = db.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    # Prevent duplicate department name within same organisation
    existing = db.query(Department).filter(
        Department.organisation_id == organisation_id,
        Department.name.ilike(name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="A department with this name already exists in this organisation"
        )

    # Validate manager
    if manager_id:
        manager = db.query(User).filter(User.id == manager_id).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager user not found")

        if manager.organisation_id != organisation_id:
            raise HTTPException(
                status_code=400,
                detail="Manager must belong to the same organisation"
            )

    # Create department
    dept = Department(
        name=name,
        organisation_id=organisation_id,
        manager_id=manager_id
    )

    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


# -------------------------------------------------------
# GET BY ID
# -------------------------------------------------------
def get_department(db: Session, department_id: UUID):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


# -------------------------------------------------------
# LIST ALL
# -------------------------------------------------------
def list_departments(db: Session):
    return db.query(Department).all()


# -------------------------------------------------------
# UPDATE DEPARTMENT
# -------------------------------------------------------
def update_department(db: Session, department_id: UUID, name: str | None, manager_id: UUID | None):
    dept = get_department(db, department_id)

    # Update name if provided
    if name:
        # Check duplicate name inside same organisation
        duplicate = db.query(Department).filter(
            Department.organisation_id == dept.organisation_id,
            Department.name.ilike(name),
            Department.id != department_id
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Another department with this name already exists in this organisation"
            )

        dept.name = name

    # Update manager
    if manager_id is not None:
        if manager_id == "":
            dept.manager_id = None  # removing manager
        else:
            manager = db.query(User).filter(User.id == manager_id).first()
            if not manager:
                raise HTTPException(status_code=404, detail="Manager not found")

            if manager.organisation_id != dept.organisation_id:
                raise HTTPException(
                    status_code=400,
                    detail="Manager must belong to the same organisation"
                )

            dept.manager_id = manager_id

    db.commit()
    db.refresh(dept)
    return dept


# -------------------------------------------------------
# DELETE
# -------------------------------------------------------
def delete_department(db: Session, department_id: UUID):
    dept = get_department(db, department_id)
    db.delete(dept)
    db.commit()
    return {"detail": "Department deleted successfully"}
