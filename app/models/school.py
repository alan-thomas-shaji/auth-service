from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, String

from app.db.base import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
