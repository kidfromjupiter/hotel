from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
    model_config = ConfigDict(extra="forbid")

    branchId: int = Field(gt=0)
    checkIn: str
    checkOut: str
    adults: int
    children: int
    nights: Optional[int] = 1
    roomNumber: int = Field(gt=0, le=32767)
    roomType: Optional[str] = None
    phone: str
    totalPrice: float
