from pydantic import BaseModel
from typing import Optional
from uuid import UUID


# ---------------------------------------------------
# BASE SCHEMA
# ---------------------------------------------------
class OrganisationBase(BaseModel):
    name: str
    address: Optional[str] = None


# ---------------------------------------------------
# CREATE ORGANISATION
# superadmin can assign admin_id or leave None
# ---------------------------------------------------
class OrganisationCreate(OrganisationBase):
    admin_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------
# READ ORGANISATION (Response)
# ---------------------------------------------------
class OrganisationRead(OrganisationBase):
    id: UUID
    employees_count: int = 0
    admin_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------
# UPDATE ORGANISATION
# ---------------------------------------------------
class OrganisationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    admin_id: Optional[UUID] = None  # allow updating admin

    class Config:
        from_attributes = True
