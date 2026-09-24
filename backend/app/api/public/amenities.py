from fastapi import APIRouter, Depends

from app.api.dependencies import get_amenities_service
from app.services.amenities_service import AmenitiesService

router = APIRouter()


@router.get("/")
@router.get("/amenities")
def get_amenities(
    branch: str = "colombo",
    amenities_service: AmenitiesService = Depends(get_amenities_service),
):
    """Public customer endpoint to fetch optional add-on amenities for a branch."""
    return amenities_service.get_amenities(branch)
