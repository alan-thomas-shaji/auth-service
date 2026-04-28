import uuid

from sqlalchemy import Column, String

from app.db.base import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)
    permission = Column(String, nullable=False)
