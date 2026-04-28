from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    tenant_id: str
    is_active: bool
