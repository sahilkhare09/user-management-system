from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List, Any
from datetime import datetime


# -------------------------------------------
# ROLE ENUM (controls allowed role values)
# -------------------------------------------
class UserRole(str):
    SUPERADMIN = "superadmin"
    ORG_ADMIN = "organisation_admin"
    DEPT_MANAGER = "department_manager"
    EMPLOYEE = "employee"


# -------------------------------------------
# USER CREATE
# -------------------------------------------
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    email: EmailStr
    password: str
    role: Optional[str] = UserRole.EMPLOYEE

    organisation_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# -------------------------------------------
# USER READ (response)
# -------------------------------------------
class UserRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    age: int
    email: EmailStr
    role: str

    organisation_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------
# USER UPDATE
# -------------------------------------------
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

    organisation_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class ExcelImportResult(BaseModel):
    success_count: int
    failed_count: int
    errors: List[Any]
