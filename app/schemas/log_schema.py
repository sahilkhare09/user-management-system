from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class LogRead(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    timestamp: datetime

    class Config:
        from_attributes = True
