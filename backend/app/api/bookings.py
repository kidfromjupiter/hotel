from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_booking_flow_service
from app.schemas.bookings import (
    BookingDetailResponse,
    BookingListItem,
    CancelBookingResponse,
    CheckInRequest,
    CheckInResponse,
    CheckOutRequest,
    CheckOutResponse,
)
from app.services.booking_flow_service import BookingFlowService

router = APIRouter()


@router.get("/", response_model=List[BookingListItem])
def list_bookings(
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    guest_id: Optional[int] = Query(None, description="Filter by guest ID"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    start_date: Optional[str] = Query(None, description="Filter bookings starting from YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Filter bookings ending before YYYY-MM-DD"),
    booking_flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Search and filter bookings."""
    return booking_flow_service.list_bookings(
        branch_id=branch_id,
        guest_id=guest_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{booking_id}", response_model=BookingDetailResponse)
def get_booking(
    booking_id: int,
    booking_flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Get full booking details including room, guest, and invoice status."""
    return booking_flow_service.get_booking_by_id(booking_id)


@router.post("/{booking_id}/check-in", response_model=CheckInResponse)
def check_in(
    booking_id: int,
    payload: Optional[CheckInRequest] = None,
    booking_flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Check a guest in, setting status to Checked-In and marking room occupied."""
    check_in_time = payload.check_in_time if payload else None
    return booking_flow_service.check_in(booking_id, check_in_time=check_in_time)


@router.post("/{booking_id}/check-out", response_model=CheckOutResponse)
def check_out(
    booking_id: int,
    payload: Optional[CheckOutRequest] = None,
    booking_flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Check a guest out. Enforces full invoice payment before checkout."""
    check_out_time = payload.check_out_time if payload else None
    return booking_flow_service.check_out(booking_id, check_out_time=check_out_time)


@router.post("/{booking_id}/cancel", response_model=CancelBookingResponse)
def cancel_booking(
    booking_id: int,
    booking_flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Cancel a booking. Rejects if booking is already Checked-In or Checked-Out."""
    return booking_flow_service.cancel_booking(booking_id)
