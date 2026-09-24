from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_flow_service
from app.schemas.booking_flow import CreateBookingRequest
from app.services.booking_flow_service import BookingFlowService

router = APIRouter()


@router.post("/")
def create_customer_booking(
    payload: CreateBookingRequest,
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    """Public customer endpoint to complete a room reservation."""
    return flow_service.create_booking(payload)
