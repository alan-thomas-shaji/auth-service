import uuid

from sqlalchemy.orm import Session

from app.models.school import School


class TenantService:
    def __init__(self, db: Session):
        self.db = db

    def create_school(self, name: str):
        school = School(id=str(uuid.uuid4()), name=name)
        self.db.add(school)
        self.db.commit()
        self.db.refresh(school)
        return school
