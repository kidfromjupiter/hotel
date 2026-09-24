from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_guests():
    """Staff/Internal endpoint to list registered guests."""
    return []
