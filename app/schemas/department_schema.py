from pydantic import BaseModel
from uuid import UUID
from typing import Optional


# -------------------------------------------------------
# BASE SCHEMA
# -------------------------------------------------------
class DepartmentBase(BaseModel):
    name: str


# -------------------------------------------------------
# CREATE DEPARTMENT
# -------------------------------------------------------
class DepartmentCreate(DepartmentBase):
    organisation_id: UUID
    manager_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# -------------------------------------------------------
# UPDATE DEPARTMENT
# -------------------------------------------------------
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    manager_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# -------------------------------------------------------
# READ / RESPONSE SCHEMA
# -------------------------------------------------------
class DepartmentRead(DepartmentBase):
    id: UUID
    organisation_id: UUID
    manager_id: Optional[UUID]

    class Config:
        from_attributes = True
