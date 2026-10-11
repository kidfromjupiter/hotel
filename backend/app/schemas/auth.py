from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class StaffUser(BaseModel):
    staff_id: int
    branch_id: Optional[int] = None
    username: str
    full_name: str
    role: str
    is_active: bool = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: StaffUser
