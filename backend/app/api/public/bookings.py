from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_service, get_current_guest_optional, get_guest_service
from app.schemas.booking_flow import CreateBookingRequest
from app.services.booking_service import BookingService
from app.services.guest_service import GuestService

router = APIRouter()


@router.post("/")
@router.post("/create")
def create_customer_booking(
    payload: CreateBookingRequest,
    booking_service: BookingService = Depends(get_booking_service),
    current_guest: Optional[Dict[str, Any]] = Depends(get_current_guest_optional),
    guest_service: GuestService = Depends(get_guest_service),
):
    """Public customer endpoint to complete a room reservation."""
    # If not authenticated, ensure we find or create the guest by phone
    token_to_use = current_guest
    g_first = payload.firstName or payload.first_name or ""
    g_last = payload.lastName or payload.last_name or ""
    combined_name = f"{g_first} {g_last}".strip() if (g_first or g_last) else None
    g_name = combined_name or payload.name or payload.guest_name
    g_nic = payload.national_id
    g_email = payload.email

    if not current_guest and payload.phone:
        guest = guest_service.lookup_by_phone(payload.phone)
        if not guest:
            guest = guest_service.create_guest(
                payload.phone,
                name=g_name or "Guest",
                national_id=g_nic,
                email=g_email,
            )
        else:
            if g_name or g_nic or g_email:
                guest_service.update_guest_info(
                    guest_id=guest["guest_id"],
                    name=g_name,
                    national_id=g_nic,
                    email=g_email,
                )
        if guest and guest.get("guest_id"):
            token_to_use = {
                "guest_id": guest["guest_id"],
                "discount_percent": guest.get("room_discount_percentage", 0),
            }
    elif current_guest and (g_name or g_nic or g_email):
        guest_service.update_guest_info(
            guest_id=current_guest.get("guest_id"),
            name=g_name,
            national_id=g_nic,
            email=g_email,
        )

    return booking_service.create_booking(payload, guest_token=token_to_use)


from app.api.dependencies import get_current_guest

@router.get("/")
def get_my_bookings(
    booking_service: BookingService = Depends(get_booking_service),
    current_guest: Dict[str, Any] = Depends(get_current_guest),
):
    """Public customer endpoint to retrieve their own reservations."""
    if not current_guest.get("guest_id"):
        return []
    return booking_service.booking_repo.list_all_bookings(guest_id=current_guest["guest_id"])
