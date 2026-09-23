from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_room_service
from app.services.room_service import RoomService

router = APIRouter()


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
