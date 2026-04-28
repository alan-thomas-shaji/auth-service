from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

from app.api.routes.auth import router as auth_router
from app.api.routes.tenant import router as tenant_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth")
app.include_router(tenant_router, prefix="/tenant")