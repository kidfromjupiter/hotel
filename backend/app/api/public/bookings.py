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
    if not current_guest and payload.phone:
        guest = guest_service.lookup_by_phone(payload.phone)
        if not guest:
            guest = guest_service.create_guest(payload.phone)
        if guest and guest.get("guest_id"):
            # Create a mock token just to pass the guest_id downstream
            token_to_use = {"guest_id": guest["guest_id"], "discount_percent": 0}

    return booking_service.create_booking(payload, guest_token=token_to_use)


from app.api.dependencies import get_current_guest
from app.schemas.booking_flow import BillCalculationRequest, BillCalculationResponse

@router.get("/")
def get_my_bookings(
    booking_service: BookingService = Depends(get_booking_service),
    current_guest: Dict[str, Any] = Depends(get_current_guest),
):
    """Public customer endpoint to retrieve their own reservations."""
    if not current_guest.get("guest_id"):
        return []
    return booking_service.booking_repo.list_all_bookings(guest_id=current_guest["guest_id"])


@router.post("/calculate-bill", response_model=BillCalculationResponse)
@router.post("/services/calculate-bill", response_model=BillCalculationResponse)
def calculate_bill_with_services(
    payload: BillCalculationRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Public endpoint after room selection to add services the guest wants and calculate whole bill.
    NOTE: Database records are intentionally NOT updated (read-only calculation/preview).
    """
    return booking_service.calculate_bill(payload)


@router.post("/{booking_id}/calculate-bill", response_model=BillCalculationResponse)
def calculate_booking_bill_with_services(
    booking_id: int,
    payload: BillCalculationRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    """
    Public endpoint to calculate whole bill with additional services for an existing booking.
    NOTE: Database records are intentionally NOT updated (read-only calculation/preview).
    """
    payload.booking_id = booking_id
    return booking_service.calculate_bill(payload)

