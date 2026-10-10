from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_booking_service, get_otp_service, get_billing_service
from app.schemas.booking_flow import CheckInOTPRequest
from app.services.otp_service import OTPService
from app.schemas.bookings import (
    AdminReservationListItem,
    BookingDetailResponse,
    BookingListItem,
    CancelBookingResponse,
    CheckInRequest,
    CheckInResponse,
    CheckOutRequest,
    CheckOutResponse,
)
from app.services.booking_service import BookingService
from app.services.billing_service import BillingService

router = APIRouter()


@router.get("/", response_model=List[BookingListItem])
def list_bookings(
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    guest_id: Optional[int] = Query(None, description="Filter by guest ID"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    start_date: Optional[date] = Query(
        None, description="Filter bookings starting from YYYY-MM-DD"
    ),
    end_date: Optional[date] = Query(
        None, description="Filter bookings ending before YYYY-MM-DD"
    ),
    booking_service: BookingService = Depends(get_booking_service),
):
    """Staff/Internal endpoint to search and filter bookings."""
    return booking_service.list_bookings(
        branch_id=branch_id,
        guest_id=guest_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/admin-reservations", response_model=List[AdminReservationListItem])
def get_admin_reservations(
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    booking_service: BookingService = Depends(get_booking_service),
):
    """Admin endpoint to search and filter bookings with financial info."""
    return booking_service.get_admin_reservations_list(
        branch_id=branch_id,
        status=status,
    )


@router.post("/verify-otp")
def verify_otp(
    payload: CheckInOTPRequest,
    otp_service: OTPService = Depends(get_otp_service),
    booking_service: BookingService = Depends(get_booking_service),
):
    """Look up a pending booking by its SKN reference or a valid OTP."""
    if payload.otp.startswith("SKN-"):
        return booking_service.get_pending_booking_by_ref(payload.otp)

    phone = otp_service.find_phone_by_otp(payload.otp)
    if phone is None:
        return {"success": False, "message": "Invalid OTP or booking not found."}

    return booking_service.get_pending_booking_by_phone(phone)


@router.get("/{booking_id}", response_model=BookingDetailResponse)
def get_booking(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
):
    """Staff/Internal endpoint to view full booking details."""
    return booking_service.get_booking_by_id(booking_id)


@router.post("/{booking_id}/check-in", response_model=CheckInResponse)
def check_in(
    booking_id: int,
    payload: Optional[CheckInRequest] = None,
    booking_service: BookingService = Depends(get_booking_service),
):
    """Staff/Receptionist endpoint to check a guest in."""
    check_in_time = payload.check_in_time if payload else None
    return booking_service.check_in(booking_id, check_in_time=check_in_time)


@router.post("/{booking_id}/check-out", response_model=CheckOutResponse)
def check_out(
    booking_id: int,
    payload: Optional[CheckOutRequest] = None,
    billing_service: BillingService = Depends(get_billing_service),
):
    """Staff/Receptionist endpoint to check a guest out (enforces full payment and releases room)."""
    check_out_time = payload.check_out_time if payload else None

    res = billing_service.checkout(booking_id, payment_method="CASH")
    
    if not res.get("success"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=res.get("message", "Check-out failed."))
        
    import datetime
    out_time = check_out_time or datetime.datetime.now().strftime("%H:%M:%S")
    
    return CheckOutResponse(
        booking_id=booking_id,
        booking_status="CHECKED_OUT",
        checked_out_time=out_time
    )


@router.post("/{booking_id}/cancel", response_model=CancelBookingResponse)
def cancel_booking(
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
):
    """Staff endpoint to cancel a booking."""
    return booking_service.cancel_booking(booking_id)
