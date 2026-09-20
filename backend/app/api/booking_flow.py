from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_flow_service
from app.schemas.booking_flow import (
    AvailabilityRequest,
)
from app.services.booking_flow_service import BookingFlowService

router = APIRouter()


@router.post("/rooms/availability")
def check_availability(
    payload: AvailabilityRequest,
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    return flow_service.check_availability(request=payload)


@router.get("/amenities")
def get_amenities(
    branch: str = "colombo",
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    return flow_service.get_amenities(branch)
