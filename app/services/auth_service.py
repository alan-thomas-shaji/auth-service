from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY
from app.models.refresh_token import RefreshToken
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, email: str, password: str, tenant_id: str):
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise Exception("User with this email already exists")

        hashed_password = security.hash_password(password)
        user = User(
            email=email,
            password=hashed_password,
            role="student",
            tenant_id=tenant_id,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login_user(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise Exception("Invalid email or password")

        if not security.verify_password(password, user.password):
            raise Exception("Invalid email or password")

        token = security.create_access_token(
            {
                "sub": user.id,
                "email": user.email,
                "role": user.role,
                "tenant_id": user.tenant_id,
                "permissions": ["VIEW_ATTENDANCE"],
            }
        )
        return token

    def generate_tokens(self, user):
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "permissions": ["VIEW_ATTENDANCE"],
        }
        access_token = security.create_access_token(payload)
        refresh_token = security.create_refresh_token(payload)

        self.db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
        refresh_record = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_record)
        self.db.commit()

        return {"access_token": access_token, "refresh_token": refresh_token}

    def refresh_access_token(self, refresh_token: str):
        token_record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token)
            .first()
        )
        if not token_record:
            raise Exception("Invalid refresh token")

        if token_record.expires_at < datetime.utcnow():
            raise Exception("Refresh token expired")

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as exc:
            raise Exception("Invalid refresh token") from exc

        new_access_token = security.create_access_token(
            {
                "sub": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "tenant_id": payload.get("tenant_id"),
                "permissions": payload.get("permissions", []),
            }
        )
        return new_access_token

    def delete_user(self, user_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("User not found")
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user

    def request_password_reset(self, email: str):
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise Exception("User not found")

        reset_token = jwt.encode(
            {
                "sub": user.id,
                "type": "password_reset",
                "exp": datetime.utcnow() + timedelta(minutes=15),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return reset_token

    def reset_password(self, token: str, new_password: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as exc:
            raise Exception("Invalid or expired reset token") from exc

        if payload.get("type") != "password_reset":
            raise Exception("Invalid reset token")

        user_id = payload.get("sub")
        if not user_id:
            raise Exception("Invalid reset token")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("User not found")

        user.password = security.hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user
