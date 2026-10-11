from fastapi import APIRouter, Depends

from app.api.dependencies import get_room_service
from app.services.room_service import RoomService

router = APIRouter()


@router.get("/all")
def get_all_rooms(
    room_service: RoomService = Depends(get_room_service),
):
    """Staff/Internal endpoint to get all rooms."""
    return room_service.get_all_rooms()
