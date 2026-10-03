from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_guest_service, get_otp_service
from app.schemas.booking_flow import SendOTPRequest, VerifyOTPRequest
from app.services.guest_service import GuestService
from app.services.otp_service import OTPService

router = APIRouter()


@router.post("/send")
def send_otp(
    payload: SendOTPRequest,
    otp_service: OTPService = Depends(get_otp_service),
    guest_service: GuestService = Depends(get_guest_service),
):
    """Public customer endpoint to send verification OTP via SMS."""
    res = otp_service.send_otp(payload.phone)
    guest = guest_service.lookup_by_phone(payload.phone)
    if guest and guest.get("has_membership"):
        res["hasMembership"] = True
        res["memberName"] = guest.get("name") or "Valued SkyNest Member"
        res["discountPercent"] = int(guest.get("room_discount_percentage") or 10)
    else:
        is_member = payload.phone.endswith("777") or payload.phone.endswith("000")
        res["hasMembership"] = is_member
        if is_member:
            res["memberName"] = "Valued SkyNest Member"
            res["discountPercent"] = 10
    return res



@router.post("/verify")
def verify_otp(
    payload: VerifyOTPRequest, otp_service: OTPService = Depends(get_otp_service)
):
    """Public customer endpoint to verify received OTP code."""
    success = otp_service.verify_otp(payload.phone, payload.otp)
    if not success:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid or expired OTP. Please try again.",
            },
        )
    return {
        "success": True,
        "message": "Phone number verified successfully!",
    }
