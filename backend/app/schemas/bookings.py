from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BookingListItem(BaseModel):
    booking_id: int
    guest_name: str
    room_number: int
    branch_name: str
    booking_status: str
    start_date: str
    end_date: str


class CheckInRequest(BaseModel):
    check_in_time: Optional[str] = Field(default=None, description="Check-in time in HH:MM:SS format")


class CheckInResponse(BaseModel):
    booking_id: int
    booking_status: str = "Checked-In"
    checked_in_time: str


class CheckOutRequest(BaseModel):
    check_out_time: Optional[str] = Field(default=None, description="Check-out time in HH:MM:SS format")


class CheckOutResponse(BaseModel):
    booking_id: int
    booking_status: str = "Checked-Out"
    checked_out_time: str


class CancelBookingResponse(BaseModel):
    booking_id: int
    booking_status: str = "Cancelled"


class GuestProfileSummary(BaseModel):
    guest_id: int
    name: str


class RoomSummary(BaseModel):
    room_number: int
    branch_name: str
    room_type_id: str


class ServiceChargeItem(BaseModel):
    service_name: str
    service_dates: int
    service_total: float


class BookingDetailResponse(BaseModel):
    booking_id: int
    guest: GuestProfileSummary
    room: RoomSummary
    booking_status: str
    start_date: str
    end_date: str
    checked_in_time: Optional[str] = None
    checked_out_time: Optional[str] = None
    adult_count: int
    children_count: int
    service_charges: List[ServiceChargeItem] = []
    invoice_status: str
    grand_total: float = 0.0
    amount_paid: float = 0.0
