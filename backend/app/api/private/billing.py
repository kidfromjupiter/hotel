from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_billing_service
from app.schemas.billing import CheckoutRequest, RecordPaymentRequest
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


@router.post("/invoices/{invoice_id}/payments", status_code=201)
def record_payment(
    invoice_id: UUID,
    payload: RecordPaymentRequest,
    billing_service: BillingService = Depends(get_billing_service),
) -> Dict[str, Any]:
    result = billing_service.record_payment(invoice_id, payload.amount, payload.payment_method)
    if not result.get("success"):
        error_code = result.get("error_code")
        status_code = 404 if error_code == "NOT_FOUND" else 409 if error_code == "INVALID_STATUS" else 400
        raise HTTPException(status_code=status_code, detail=result.get("message", "Payment failed."))
    return result


@router.post("/checkout")
def checkout_stay(
    payload: CheckoutRequest,
    billing_service: BillingService = Depends(get_billing_service),
) -> Dict[str, Any]:
    """Staff/Internal endpoint to process guest stay checkout, room release, and invoice finalization."""
    result = billing_service.checkout(booking_id=payload.booking_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=400, detail=result.get("message", "Checkout failed")
        )
    return result
