from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SendOTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
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
    totalPrice: float
    amenityIds: Optional[List[str]] = []
    amenities: Optional[List[Dict[str, Any]]] = []
