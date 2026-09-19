from app.repositories.booking_flow_repo import BookingFlowRepository
from app.services.booking_flow_service import BookingFlowService
from app.services.otp_service import OTPService

# TODO: Make these stateless. That means removing the singleton pattern
booking_flow_repo = BookingFlowRepository()
booking_flow_service = BookingFlowService(booking_flow_repo=booking_flow_repo)
otp_service = OTPService()


def get_booking_flow_repo() -> BookingFlowRepository:
    return booking_flow_repo
    # return BookingFlowRepository()


def get_booking_flow_service() -> BookingFlowService:
    return booking_flow_service
    # return BookingFlowService(booking_flow_repo=get_booking_flow_repo())


def get_otp_service() -> OTPService:
    return otp_service
    # return OTPService()
