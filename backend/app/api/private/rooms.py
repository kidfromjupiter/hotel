from fastapi import APIRouter, Depends

from app.api.dependencies import get_room_service, require_admin
from app.schemas.rooms import CreateRoomRequest
from app.services.room_service import RoomService

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/types")
def list_room_types(
    service: RoomService = Depends(get_room_service),
):
    return service.get_room_types()


@router.post("/", status_code=201)
def create_room(
    payload: CreateRoomRequest,
    service: RoomService = Depends(get_room_service),
):
    return service.create_room(payload)
