from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_billing_service
from app.schemas.billing import CheckoutRequest
from app.services.billing_service import BillingService

router = APIRouter()


@router.get("/invoices")
def list_invoices(
    payment_status: Optional[str] = Query(
        None, description="Filter by payment status (e.g., PAID, PARTIALLY_PAID)"
    ),
    billing_service: BillingService = Depends(get_billing_service),
) -> List[Dict[str, Any]]:
    """Staff/Internal endpoint to list guest billing summaries and invoices."""
    return billing_service.list_invoices(payment_status=payment_status)


@router.get("/stays/active")
def list_active_stays(
    billing_service: BillingService = Depends(get_billing_service),
) -> List[Dict[str, Any]]:
    """Staff/Internal endpoint to list currently checked-in active stays."""
    return billing_service.list_active_stays()


@router.post("/checkout")
def checkout_stay(
    payload: CheckoutRequest,
    billing_service: BillingService = Depends(get_billing_service),
) -> Dict[str, Any]:
    """Staff/Internal endpoint to process guest stay checkout, room release, and invoice finalization."""
    result = billing_service.checkout(
        booking_id=payload.booking_id,
        payment_method=payload.payment_method or "CREDIT_CARD",
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("message", "Checkout failed")
        )
    return result
