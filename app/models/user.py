from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="Employee")

    organisation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id"),
        nullable=True
    )

    department_id = Column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        nullable=True
    )

    # RELATIONSHIPS FIX
    organisation = relationship(
        "Organisation",
        back_populates="users",
        foreign_keys=[organisation_id]
    )

    logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True
    )

    created_at = Column(DateTime, default=datetime.utcnow)
