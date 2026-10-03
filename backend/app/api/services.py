from fastapi import APIRouter, Depends

from app.api.dependencies import get_service_service
from app.services.service_service import ServiceService

router = APIRouter()


@router.get("/")
def list_services(service: ServiceService = Depends(get_service_service)):
    return service.get_all_services()
