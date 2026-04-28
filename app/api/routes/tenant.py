from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.school import SchoolCreateRequest, SchoolResponse
from app.services.tenant_service import TenantService

router = APIRouter()


@router.post("/onboard", response_model=SchoolResponse)
def onboard_school(payload: SchoolCreateRequest, db: Session = Depends(get_db)):
    service = TenantService(db)
    try:
        school = service.create_school(name=payload.name)
        return SchoolResponse(id=school.id, name=school.name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
