from typing import List, Optional
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


class GuestPaymentProfile(BaseModel):
    guest_id: int
    name: str
    phone_number: str


class GuestPaymentSummary(BaseModel):
    booking_count: int
    grand_total: float
    amount_paid: float
    outstanding_balance: float


class GuestPaymentBooking(BaseModel):
    booking_id: int
    booking_ref: str
    branch_id: Optional[int] = None
    branch_name: str
    start_date: str
    end_date: str
    booking_status: str
    invoice_id: Optional[str] = None
    payment_method: str
    payment_status: str
    grand_total: float
    amount_paid: float
    outstanding_balance: float


class GuestPaymentHistoryResponse(BaseModel):
    guest: GuestPaymentProfile
    summary: GuestPaymentSummary
    bookings: List[GuestPaymentBooking]
