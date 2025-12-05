from pydantic import BaseModel
from typing import Optional
from uuid import UUID



class OrganisationBase(BaseModel):
    name: str
    address: Optional[str] = None




class OrganisationCreate(OrganisationBase):
    admin_id: Optional[UUID] = None

    class Config:
        from_attributes = True



class OrganisationRead(OrganisationBase):
    id: UUID
    employees_count: int = 0
    admin_id: Optional[UUID] = None

    class Config:
        from_attributes = True



class OrganisationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    admin_id: Optional[UUID] = None

    class Config:
        from_attributes = True
