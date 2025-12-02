from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.organisation import Organisation


# -------------------------------------------------------
# CREATE ORGANISATION
# -------------------------------------------------------
def create_organisation(db: Session, payload):
    # Check duplicate organisation name
    existing = db.query(Organisation).filter(
        Organisation.name.ilike(payload.name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Organisation with this name already exists"
        )

    org = Organisation(**payload.dict())

    db.add(org)
    db.commit()
    db.refresh(org)
    return org


# -------------------------------------------------------
# LIST ORGANISATIONS
# -------------------------------------------------------
def list_organisations(db: Session):
    return db.query(Organisation).all()


# -------------------------------------------------------
# GET ORGANISATION BY ID
# -------------------------------------------------------
def get_organisation(db: Session, organisation_id: UUID):
    org = db.query(Organisation).filter(
        Organisation.id == organisation_id
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    return org


# -------------------------------------------------------
# UPDATE ORGANISATION
# -------------------------------------------------------
def update_organisation(db: Session, organisation_id: UUID, payload):
    org = get_organisation(db, organisation_id)

    update_data = payload.dict(exclude_unset=True)

    # If updating name → check duplicate
    if "name" in update_data:
        existing = db.query(Organisation).filter(
            Organisation.name.ilike(update_data["name"]),
            Organisation.id != organisation_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Another organisation with this name already exists"
            )

    # Apply updates safely
    for key, value in update_data.items():
        setattr(org, key, value)

    db.commit()
    db.refresh(org)
    return org


# -------------------------------------------------------
# DELETE ORGANISATION
# -------------------------------------------------------
def delete_organisation(db: Session, organisation_id: UUID):
    org = get_organisation(db, organisation_id)

    db.delete(org)
    db.commit()

    return {"message": "Organisation deleted successfully"}
