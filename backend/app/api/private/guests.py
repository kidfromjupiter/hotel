from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_guest_service
from app.schemas.guests import EnrollMembershipRequest, UpdatePhoneRequest, CreateMembershipPayload
from app.services.guest_service import GuestService

router = APIRouter()


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

@router.post("/memberships")
def create_membership(
    payload: CreateMembershipPayload,
    guest_service: GuestService = Depends(get_guest_service),
) -> Dict[str, Any]:
    """Enroll a new or existing guest into SkyNest membership program via frontend form."""
    result = guest_service.enroll_by_phone(name=payload.name, phone=payload.phone, email=payload.email)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to create membership"))
    return result
