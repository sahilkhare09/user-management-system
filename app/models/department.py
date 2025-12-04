from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.db import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)

    organisation_id = Column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False
    )
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


    organisation = relationship("Organisation", back_populates="departments")

    manager = relationship("User", foreign_keys=[manager_id])
