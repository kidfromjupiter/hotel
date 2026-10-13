from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import (
    enforce_branch_access,
    get_current_user,
    get_guest_service,
)
from app.schemas.auth import StaffUser
from app.schemas.guests import (
    EnrollMembershipRequest,
    GuestPaymentHistoryResponse,
    UpdatePhoneRequest,
)
from app.services.guest_service import GuestService

router = APIRouter()


@router.get("/payment-status", response_model=GuestPaymentHistoryResponse)
def get_guest_payment_status(
    query: str = Query(..., min_length=1, description="Exact guest ID or phone number"),
    guest_service: GuestService = Depends(get_guest_service),
    current_user: StaffUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return a guest's booking and invoice history within the staff member's branch scope."""
    branch_id = enforce_branch_access(None, current_user)
    result = guest_service.get_payment_history(query=query, branch_id=branch_id)
    if not result:
        raise HTTPException(status_code=404, detail="Guest not found")
    return result


@router.get("/")
def list_guests(
    search: Optional[str] = Query(None, description="Search by name, NIC, or phone"),
    guest_service: GuestService = Depends(get_guest_service),
) -> List[Dict[str, Any]]:
    """Staff/Internal endpoint to list registered guests with membership details."""
    return guest_service.list_guests(search=search)


@router.get("/lookup/phone")
def lookup_guest_by_phone(
    phone: str = Query(..., description="Phone number to lookup"),
    guest_service: GuestService = Depends(get_guest_service),
) -> Dict[str, Any]:
    """Lookup guest and SkyNest membership status by phone number."""
    guest = guest_service.lookup_by_phone(phone=phone)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


@router.get("/{guest_id}")
def get_guest(
    guest_id: int,
    guest_service: GuestService = Depends(get_guest_service),
) -> Dict[str, Any]:
    """Get single guest details and membership status."""
    guest = guest_service.get_guest(guest_id=guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


@router.put("/{guest_id}/phone")
def update_guest_phone(
    guest_id: int,
    payload: UpdatePhoneRequest,
    guest_service: GuestService = Depends(get_guest_service),
) -> Dict[str, Any]:
    """Update a guest's contact phone number."""
    result = guest_service.update_phone(guest_id=guest_id, phone=payload.phone)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to update phone"))
    return result


@router.post("/{guest_id}/membership")
def enroll_guest_membership(
    guest_id: int,
    payload: EnrollMembershipRequest,
    guest_service: GuestService = Depends(get_guest_service),
) -> Dict[str, Any]:
    """Enroll a guest into SkyNest membership program."""
    result = guest_service.enroll_membership(guest_id=guest_id, membership_id=payload.membership_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to enroll in membership"))
    return result
