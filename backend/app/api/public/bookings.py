from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_booking_service, get_current_guest, get_guest_service
from app.schemas.booking_flow import CreateBookingRequest
from app.services.booking_service import BookingService
from app.services.guest_service import GuestService

router = APIRouter()


@router.post("/")
@router.post("/create")
def create_customer_booking(
    payload: CreateBookingRequest,
    booking_service: BookingService = Depends(get_booking_service),
    guest_service: GuestService = Depends(get_guest_service),
):
    """Public customer endpoint to complete a room reservation."""
    # Price and membership are resolved from the guest identified by this phone.
    guest = guest_service.lookup_by_phone(payload.phone)
    if not guest:
        guest = guest_service.create_guest(payload.phone)
    if not guest:
        raise HTTPException(status_code=422, detail="Enter a valid phone number.")
    return booking_service.create_booking(
        payload, guest_token={"guest_id": guest["guest_id"]}
    )


@router.get("/")
def get_my_bookings(
    booking_service: BookingService = Depends(get_booking_service),
    current_guest: Dict[str, Any] = Depends(get_current_guest),
):
    """Public customer endpoint to retrieve their own reservations."""
    if not current_guest.get("guest_id"):
        return []
    return booking_service.list_guest_bookings(current_guest["guest_id"])
