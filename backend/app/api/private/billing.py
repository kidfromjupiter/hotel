from fastapi import APIRouter

router = APIRouter()


@router.get("/invoices")
def list_invoices():
    """Staff/Internal endpoint to list guest invoices."""
    return []
