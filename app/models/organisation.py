from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.db import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=True)
    employees_count = Column(Integer, default=0)

    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # ----------------------------
    # RELATIONSHIPS (FINAL FIX)
    # ----------------------------

    users = relationship(
        "User",
        back_populates="organisation",
        foreign_keys="User.organisation_id",
        cascade="all, delete"
    )

    admin = relationship(
        "User",
        foreign_keys=[admin_id]
    )

    departments = relationship(
        "Department",
        back_populates="organisation",
        cascade="all, delete"
    )
