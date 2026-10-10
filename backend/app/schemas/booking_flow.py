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


class ServiceItemSelection(BaseModel):
    service_id: Optional[int] = None
    service_name: Optional[str] = None
    quantity: int = 1
    days: int = 1
    unit_price: Optional[float] = None


class BillCalculationRequest(BaseModel):
    booking_id: Optional[int] = None
    branch: Optional[str] = "colombo"
    room_number: Optional[int] = None
    room_type: Optional[str] = "Standard Room"
    nights: Optional[int] = 1
    daily_rate: Optional[float] = None
    guest_phone: Optional[str] = None
    membership_discount_percent: Optional[float] = 0.0
    services: Optional[List[ServiceItemSelection]] = []


class ServiceItemBreakdown(BaseModel):
    service_id: Optional[int] = None
    service_name: str
    quantity: int
    days: int
    day_rate: float
    subtotal: float
    discount_percentage: float = 0.0
    discount_amount: float = 0.0
    total: float


class TaxBreakdownItem(BaseModel):
    tax_name: str
    tax_percentage: float
    tax_amount: float


class BillCalculationResponse(BaseModel):
    booking_id: Optional[int] = None
    room_charges: Dict[str, Any]
    services_charges: Dict[str, Any]
    taxes: List[TaxBreakdownItem]
    subtotal: float
    total_tax: float
    grand_total: float
    is_updated: bool = False
    status: str = "PREVIEW_CALCULATED"
    note: str = "Calculated bill preview with selected services. Database records remain un-updated so this can be resolved/finalized later."

