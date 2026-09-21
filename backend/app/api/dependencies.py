from fastapi import Depends
from psycopg2.extensions import connection

from app.db import get_db
from app.repositories.booking_repo import BookingRepository
from app.repositories.rooms_repo import RoomsRepo
from app.services.booking_service import BookingService
from app.services.otp_service import OTPService
from app.services.report_service import ReportService
from app.services.room_service import RoomService

# TODO: Make these stateless. That means removing the singleton pattern
report_service = ReportService()
booking_repo = BookingRepository()
booking_service = BookingService(booking_repo=booking_repo)


def get_room_repo(db: connection = Depends(get_db)) -> RoomsRepo:
    return RoomsRepo(db=db)


def get_room_service(room_repo: RoomsRepo = Depends(get_room_repo)) -> RoomService:
    return RoomService(repo=room_repo)


def get_report_service() -> ReportService:
    return report_service


def get_booking_repo() -> BookingRepository:
    return booking_repo
    # return BookingRepository()


def get_booking_service() -> BookingService:
    return booking_service
    # return BookingService(booking_repo=get_booking_repo())


def get_otp_service() -> OTPService:
    return OTPService()
