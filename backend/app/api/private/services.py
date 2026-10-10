from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_services_service
from app.schemas.services import ChargeServiceRequest
from app.services.services_service import ServicesService

router = APIRouter()


@router.get("/")
def list_services(
    services_service: ServicesService = Depends(get_services_service),
) -> List[Dict[str, Any]]:
    """Staff/Internal endpoint to list available hotel services from catalogue."""
    return services_service.list_services()


@router.post("/charge")
def charge_service(
    payload: ChargeServiceRequest,
    services_service: ServicesService = Depends(get_services_service),
) -> Dict[str, Any]:
    """Staff/Internal endpoint to charge a service to a guest stay."""
    result = services_service.charge_service(
        booking_id=payload.booking_id,
        service_id=payload.service_id,
        service_dates=payload.service_dates or 1,
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("message", "Failed to charge service")
        )
    return result
