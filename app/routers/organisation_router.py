from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.organisation_schema import (
    OrganisationCreate,
    OrganisationRead,
    OrganisationUpdate,
)
from app.database.db import get_db
from app.services.organisation_service import (
    create_organisation,
    list_organisations,
    get_organisation,
    update_organisation,
    delete_organisation,
)
from app.core.security import get_current_user, require_role

router = APIRouter(prefix="/api/v1/organisations", tags=["Organisations"])


@router.post("/", response_model=OrganisationRead)
def create_organisation_api(
    payload: OrganisationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["superadmin"])),
):
    return create_organisation(db, payload)


@router.get("/", response_model=list[OrganisationRead])
def list_organisations_api(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):

    # Superadmin sees all organisations
    if current_user.role.lower() == "superadmin":
        return list_organisations(db)

    # Organisation Admin sees only their own organisation
    if current_user.role.lower() == "organisation_admin":
        org = get_organisation(db, current_user.organisation_id)
        if not org:
            raise HTTPException(404, "Your organisation not found")
        return [org]

    # Normal user cannot list all organisations
    raise HTTPException(
        status_code=403,
        detail="Access denied. Only superadmin or organisation admin can view organisations.",
    )


@router.get("/{organisation_id}", response_model=OrganisationRead)
def get_organisation_api(
    organisation_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    org = get_organisation(db, organisation_id)
    if not org:
        raise HTTPException(404, "Organisation not found")

    # Superadmin can access any
    if current_user.role.lower() == "superadmin":
        return org

    # Organisation admin -> only their own org
    if current_user.role.lower() == "organisation_admin":
        if current_user.organisation_id == organisation_id:
            return org
        raise HTTPException(403, "You are not allowed to access another organisation")

    # Normal user cannot view organisation details
    raise HTTPException(403, "Only admins can access organisation details")


@router.put("/{organisation_id}", response_model=OrganisationRead)
def update_organisation_api(
    organisation_id: UUID,
    payload: OrganisationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["superadmin"])),
):
    org = get_organisation(db, organisation_id)
    if not org:
        raise HTTPException(404, "Organisation not found")

    return update_organisation(db, organisation_id, payload)


@router.delete("/{organisation_id}")
def delete_organisation_api(
    organisation_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["superadmin"])),
):

    org = get_organisation(db, organisation_id)
    if not org:
        raise HTTPException(404, "Organisation not found")

    return delete_organisation(db, organisation_id)
