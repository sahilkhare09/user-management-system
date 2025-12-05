from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from typing import Optional


from app.models.department import Department
from app.models.organisation import Organisation
from app.models.user import User


def create_department(
    db: Session, name: str, organisation_id: UUID, manager_id: Optional[UUID] = None
):

    org = db.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    existing = (
        db.query(Department)
        .filter(
            Department.organisation_id == organisation_id, Department.name.ilike(name)
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="A department with this name already exists in this organisation",
        )

    if manager_id:
        manager = db.query(User).filter(User.id == manager_id).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager user not found")

        if manager.organisation_id != organisation_id:
            raise HTTPException(
                status_code=400, detail="Manager must belong to the same organisation"
            )

    dept = Department(name=name, organisation_id=organisation_id, manager_id=manager_id)

    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def get_department(db: Session, department_id: UUID):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


def list_departments(db: Session):
    return db.query(Department).all()


def update_department(
    db: Session,
    department_id: UUID,
    name: Optional[str] = None,
    manager_id: Optional[UUID] = None,
):
    dept = get_department(db, department_id)

    if name:
        duplicate = (
            db.query(Department)
            .filter(
                Department.organisation_id == dept.organisation_id,
                Department.name.ilike(name),
                Department.id != department_id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Another department with this name already exists in this organisation",
            )

        dept.name = name

    if manager_id is not None:
        if manager_id == "":
            dept.manager_id = None
        else:
            manager = db.query(User).filter(User.id == manager_id).first()
            if not manager:
                raise HTTPException(status_code=404, detail="Manager not found")

            if manager.organisation_id != dept.organisation_id:
                raise HTTPException(
                    status_code=400,
                    detail="Manager must belong to the same organisation",
                )

            dept.manager_id = manager_id

    db.commit()
    db.refresh(dept)
    return dept


def delete_department(db: Session, department_id: UUID):
    dept = get_department(db, department_id)
    db.delete(dept)
    db.commit()
    return {"detail": "Department deleted successfully"}
