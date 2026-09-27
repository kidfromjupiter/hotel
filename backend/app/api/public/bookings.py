from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_service
from app.schemas.booking_flow import CreateBookingRequest
from app.services.booking_service import BookingService

router = APIRouter()


@router.post("/")
def create_customer_booking(
    payload: CreateBookingRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    """Public customer endpoint to complete a room reservation."""
    return booking_service.create_booking(payload)
