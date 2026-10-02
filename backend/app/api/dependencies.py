from fastapi import Depends
from psycopg2.extensions import connection

from app.db import get_db
from app.repositories.booking_repo import BookingRepository
from app.repositories.rooms_repo import RoomsRepo
from app.repositories.services_repo import ServicesRepo
from app.repositories.guests_repo import GuestsRepo
from app.repositories.branches_repo import BranchesRepo
from app.services.booking_service import BookingService
from app.services.otp_service import OTPService
from app.services.report_service import ReportService
from app.services.room_service import RoomService
from app.services.service_service import ServiceService
from app.services.guest_service import GuestService
from app.services.branch_service import BranchService

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


def get_services_repo(db: connection = Depends(get_db)) -> ServicesRepo:
    return ServicesRepo(db=db)


def get_service_service(
    repo: ServicesRepo = Depends(get_services_repo),
) -> ServiceService:
    return ServiceService(repo=repo)


def get_guests_repo(db: connection = Depends(get_db)) -> GuestsRepo:
    return GuestsRepo(db=db)


def get_guest_service(
    repo: GuestsRepo = Depends(get_guests_repo),
) -> GuestService:
    return GuestService(repo=repo)


def get_branches_repo(db: connection = Depends(get_db)) -> BranchesRepo:
    return BranchesRepo(db=db)


def get_branch_service(
    repo: BranchesRepo = Depends(get_branches_repo),
) -> BranchService:
    return BranchService(repo=repo)
