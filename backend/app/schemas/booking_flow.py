from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SendOTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

class CheckInOTPRequest(BaseModel):
    otp: str

    
class AvailabilityRequest(BaseModel):
    branch: str
    checkIn: str
    checkOut: str
    adults: int
    children: int


class CreateBookingRequest(BaseModel):
    branch: str
    checkIn: str
    checkOut: str
    adults: int
    children: int
    nights: Optional[int] = 1
    roomId: str
    roomType: Optional[str] = None
    phone: str
    name: Optional[str] = None
    guest_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    national_id: Optional[str] = None
    special_requests: Optional[str] = None
    specialRequests: Optional[str] = None
    totalPrice: float
    amenityIds: Optional[List[str]] = []
    amenities: Optional[List[Dict[str, Any]]] = []
