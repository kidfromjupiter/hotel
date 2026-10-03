from typing import Optional
from pydantic import BaseModel


class GuestResponse(BaseModel):
    guest_id: int
    name: str
    national_id: Optional[str] = None
    phone_number: str
    membership_id: Optional[int] = None
    membership_name: Optional[str] = "None"
    room_discount_percentage: float = 0.0
    service_discount_percentage: float = 0.0


class UpdatePhoneRequest(BaseModel):
    phone: str


class EnrollMembershipRequest(BaseModel):
    membership_id: int = 1
