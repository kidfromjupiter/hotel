from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_booking_flow_service, get_otp_service
from app.schemas.booking_flow import (
    AvailabilityRequest,
    CreateBookingRequest,
    SendOTPRequest,
    VerifyOTPRequest,
)
from app.services.booking_flow_service import BookingFlowService
from app.services.otp_service import OTPService

router = APIRouter()


@router.post("/rooms/availability")
def check_availability(
    payload: AvailabilityRequest,
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    return flow_service.check_availability(request=payload)


@router.get("/amenities")
def get_amenities(
    branch: str = "colombo",
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    return flow_service.get_amenities(branch)


@router.post("/otp/send")
def send_otp(
    payload: SendOTPRequest, otp_service: OTPService = Depends(get_otp_service)
):
    res = otp_service.send_otp(payload.phone)
    # Check mock VIP/membership for demo phones or standard
    is_member = payload.phone.endswith("777") or payload.phone.endswith("000")
    res["hasMembership"] = is_member
    if is_member:
        res["memberName"] = "Valued SkyNest Member"
        res["discountPercent"] = 10
    return res


@router.post("/otp/verify")
def verify_otp(
    payload: VerifyOTPRequest, otp_service: OTPService = Depends(get_otp_service)
):
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


@router.post("/booking/create")
def create_booking(
    payload: CreateBookingRequest,
    flow_service: BookingFlowService = Depends(get_booking_flow_service),
):
    return flow_service.create_booking(payload)
