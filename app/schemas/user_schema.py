from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    first_name : str
    last_name : str
    age : int
    email : EmailStr
    password : str

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id : UUID
    first_name : str
    last_name : str
    age : int
    email : EmailStr
    password : str
    role : str
    department : str | None = None
    organisation_id : str | None = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    department: str | None = None
    organisation_id: str | None = None

    class Config:
        from_attributes = True




