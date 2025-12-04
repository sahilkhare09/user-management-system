from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    organisation_id: UUID
    manager_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    manager_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class DepartmentRead(DepartmentBase):
    id: UUID
    organisation_id: UUID
    manager_id: Optional[UUID]

    class Config:
        from_attributes = True
