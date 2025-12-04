from pydantic import BaseModel, EmailStr
from typing import Optional



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    sub: Optional[str] = None  # user_id
    exp: Optional[int] = None  # NEW (expiry timestamp)



class RefreshRequest(BaseModel):
    refresh_token: str     # NEW
