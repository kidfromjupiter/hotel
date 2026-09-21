from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_service
from app.services.booking_service import BookingService

router = APIRouter()


# Should amenities be in the booking service anyway?
@router.get("/amenities")
def get_amenities(
    branch: str = "colombo",
    flow_service: BookingService = Depends(get_booking_service),
):
    return flow_service.get_amenities(branch)
