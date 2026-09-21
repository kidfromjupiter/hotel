from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_service
from app.schemas.booking_flow import (
    AvailabilityRequest,
)
from app.services.booking_service import BookingService

router = APIRouter()


@router.post("/rooms/availability")
def check_availability(
    payload: AvailabilityRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    return booking_service.check_availability(request=payload)
