from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_flow_service
from app.services.booking_flow_service import BookingFlowService

router = APIRouter()


@router.get("/")
@router.get("/amenities")
def get_amenities(
    branch: str = "colombo",
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Public customer endpoint to fetch optional add-on amenities for a branch."""
    return flow_service.get_amenities(branch)
