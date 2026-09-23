from typing import Optional
from fastapi import Depends
from psycopg2.extensions import connection

from app.db import get_db
from app.repositories.amenities_repo import AmenitiesRepo
from app.repositories.booking_repo import BookingRepository
from app.repositories.branches_repo import BranchesRepo
from app.repositories.rooms_repo import RoomsRepo
from app.services.amenities_service import AmenitiesService
from app.services.booking_flow_service import BookingFlowService
from app.services.booking_service import BookingService
from app.services.branch_service import BranchService
from app.services.otp_service import OTPService
from app.services.report_service import ReportService
from app.services.room_service import RoomService


# TODO: Make these stateless. That means removing the singleton pattern
report_service = ReportService()
booking_repo = BookingRepository()
booking_service = BookingService(booking_repo=booking_repo)
booking_flow_service = BookingFlowService(booking_repo=booking_repo)


otp_service = OTPService()


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


def get_booking_flow_service() -> BookingFlowService:
    return booking_flow_service


def get_otp_service() -> OTPService:
    return otp_service


def get_branches_repo(db: Optional[connection] = Depends(get_db)) -> BranchesRepo:
    return BranchesRepo(db=db)


def get_branch_service(
    branches_repo: BranchesRepo = Depends(get_branches_repo),
) -> BranchService:
    return BranchService(repo=branches_repo)


def get_amenities_repo(db: Optional[connection] = Depends(get_db)) -> AmenitiesRepo:
    return AmenitiesRepo(db=db)


def get_amenities_service(
    amenities_repo: AmenitiesRepo = Depends(get_amenities_repo),
) -> AmenitiesService:
    return AmenitiesService(repo=amenities_repo)




