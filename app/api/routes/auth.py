from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register_user(
            email=payload.email,
            password=payload.password,
            tenant_id=payload.tenant_id,
        )
        return {"message": "User registered successfully", "user_id": user.id}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        token = service.login_user(email=payload.email, password=payload.password)
        return TokenResponse(access_token=token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/verify")
def verify(current_user: dict = Depends(get_current_user)):
    return {"valid": True, "user": current_user}


@router.get("/protected")
def protected(_: dict = Depends(require_permission("VIEW_ATTENDANCE"))):
    return {"message": "Access granted"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        access_token = service.refresh_access_token(payload.refresh_token)
        return TokenResponse(access_token=access_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.delete("/delete-account")
def delete_account(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    service = AuthService(db)
    try:
        service.delete_user(current_user.get("sub"))
        return {"message": "Account deleted successfully"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/request-password-reset")
def request_password_reset(
    payload: RequestPasswordResetRequest, db: Session = Depends(get_db)
):
    service = AuthService(db)
    try:
        reset_token = service.request_password_reset(payload.email)
        return {"reset_token": reset_token}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        service.reset_password(token=payload.token, new_password=payload.new_password)
        return {"message": "Password reset successful"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
