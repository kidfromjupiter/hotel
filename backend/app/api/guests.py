# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends

from app.api.dependencies import get_guest_service
from app.services.guest_service import GuestService

router = APIRouter()


@router.get("/")
def list_guests(service: GuestService = Depends(get_guest_service)):
    return service.get_all_guests()
