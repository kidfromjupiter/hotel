from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.repositories.booking_flow_repo import booking_flow_repo
from app.services.otp_service import otp_service

router = APIRouter()


class AvailabilityRequest(BaseModel):
    branch: str
    checkIn: str
    checkOut: str
    adults: int
    children: int


class SendOTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


class CreateBookingRequest(BaseModel):
    branch: str
    checkIn: str
    checkOut: str
    adults: int
    children: int
    nights: Optional[int] = 1
    roomId: str
    roomType: Optional[str] = None
    phone: str
    totalPrice: float
    amenityIds: Optional[List[str]] = []
    amenities: Optional[List[Dict[str, Any]]] = []


@router.post("/rooms/availability")
def check_availability(payload: AvailabilityRequest):
    total_guests = payload.adults + payload.children
    all_rooms = booking_flow_repo.get_rooms_catalog(payload.branch)

    max_capacity_any_room = max((r.get("maxCapacity", 2) for r in all_rooms), default=2)
    if total_guests > max_capacity_any_room:
        return {
            "available": False,
            "rooms": [],
            "message": f"Maximum capacity exceeded. Maximum capacity per room is {max_capacity_any_room} guests.",
        }

    # Calculate nights
    try:
        d_in = datetime.fromisoformat(payload.checkIn.replace("Z", "+00:00")).date()
        d_out = datetime.fromisoformat(payload.checkOut.replace("Z", "+00:00")).date()
        nights = (d_out - d_in).days
    except Exception:
        nights = 1
    if nights < 1:
        nights = 1

    available_rooms = []
    for room in all_rooms:
        if room.get("maxCapacity", 2) < total_guests:
            continue
        if booking_flow_repo.is_room_booked(room["id"], payload.checkIn, payload.checkOut):
            continue

        r_data = dict(room)
        r_data["nights"] = nights
        r_data["totalPrice"] = r_data["pricePerNight"] * nights
        available_rooms.append(r_data)

    return {
        "available": len(available_rooms) > 0,
        "rooms": available_rooms,
        "message": "Rooms available" if available_rooms else "No rooms available for the selected dates.",
    }


@router.get("/amenities")
def get_amenities(branch: str = "colombo"):
    amenities = booking_flow_repo.get_amenities_catalog(branch)
    return {"amenities": amenities}


@router.post("/otp/send")
def send_otp(payload: SendOTPRequest):
    res = otp_service.send_otp(payload.phone)
    # Check mock VIP/membership for demo phones or standard
    is_member = payload.phone.endswith("777") or payload.phone.endswith("000")
    res["hasMembership"] = is_member
    if is_member:
        res["memberName"] = "Valued SkyNest Member"
        res["discountPercent"] = 10
    return res


@router.post("/otp/verify")
def verify_otp(payload: VerifyOTPRequest):
    success = otp_service.verify_otp(payload.phone, payload.otp)
    if not success:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Invalid or expired OTP. Please try again."},
        )
    return {
        "success": True,
        "message": "Phone number verified successfully!",
    }


@router.post("/booking/create")
def create_booking(payload: CreateBookingRequest):
    booking_dict = payload.model_dump()
    saved = booking_flow_repo.save_booking(booking_dict)
    return {
        "success": True,
        "bookingRef": saved["bookingRef"],
        "message": "Your reservation has been confirmed successfully!",
    }
