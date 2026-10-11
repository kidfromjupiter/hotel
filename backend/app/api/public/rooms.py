from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_booking_service, get_room_service
from app.schemas.booking_flow import AvailabilityRequest
from app.services.booking_service import BookingService
from app.services.room_service import RoomService

router = APIRouter()

@router.get("/all")
def get_all_rooms(
    room_service: RoomService = Depends(get_room_service),
):
    """Admin/Public endpoint to get all rooms."""
    return room_service.get_all_rooms()


@router.get("/")
@router.get("/rooms")
def check_availability(
    check_in: Optional[date] = Query(
        None, description="Filter rooms starting from YYYY-MM-DD"
    ),
    check_out: Optional[date] = Query(
        None, description="Filter rooms ending before YYYY-MM-DD"
    ),
    adults: Optional[int] = Query(None, description="No. of adults"),
    children: Optional[int] = Query(None, description="No. of children"),
    branch: Optional[str] = Query(None, description="Filter rooms by branch"),
    room_service: RoomService = Depends(get_room_service),
):
    """Public customer endpoint to check room availability across branches."""
    return room_service.get_rooms(check_in, check_out, branch, children, adults)


@router.post("/availability")
@router.post("/")
def check_availability_post(
    payload: AvailabilityRequest,
    booking_service: BookingService = Depends(get_booking_service),
):
    """Public customer endpoint to check room availability via POST payload."""
    return booking_service.check_availability(payload)
