from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_services():
    """Staff/Internal endpoint to list available hotel services."""
    return []
