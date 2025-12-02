from pydantic import BaseModel, EmailStr
from typing import Optional


# -------------------------------------------------------
# TOKEN RESPONSE (for login API)
# -------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------------------------------------------
# LOGIN REQUEST BODY
# -------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -------------------------------------------------------
# TOKEN PAYLOAD (decoded JWT)
# -------------------------------------------------------
class TokenData(BaseModel):
    sub: Optional[str] = None   # user_id

