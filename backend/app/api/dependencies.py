from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extensions import connection

from app.core.security import decode_access_token


from app.db import get_db
from app.repositories.billing_repo import BillingRepo
from app.repositories.booking_repo import BookingRepository
from app.repositories.branches_repo import BranchesRepo
from app.repositories.guests_repo import GuestsRepo
from app.repositories.reports_repo import ReportsRepo
from app.repositories.rooms_repo import RoomsRepo
from app.repositories.services_repo import ServicesRepo
from app.services.billing_service import BillingService
from app.services.booking_service import BookingService
from app.services.branch_service import BranchService
from app.services.guest_service import GuestService
from app.services.otp_service import OTPService
from app.services.report_service import ReportService
from app.services.room_service import RoomService
from app.services.services_service import ServicesService

otp_service = OTPService()


def get_room_repo(db: Optional[connection] = Depends(get_db)) -> RoomsRepo:
    return RoomsRepo(db=db)


def get_room_service(room_repo: RoomsRepo = Depends(get_room_repo)) -> RoomService:
    return RoomService(repo=room_repo)


def get_report_repo(db: Optional[connection] = Depends(get_db)) -> ReportsRepo:
    return ReportsRepo(db=db)


def get_report_service(
    report_repo: ReportsRepo = Depends(get_report_repo),
) -> ReportService:
    return ReportService(repo=report_repo)


def get_booking_repo(db: Optional[connection] = Depends(get_db)) -> BookingRepository:
    return BookingRepository(db=db)


def get_booking_service(
    booking_repo: BookingRepository = Depends(get_booking_repo),
) -> BookingService:
    return BookingService(booking_repo=booking_repo)


def get_booking_flow_service(
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingService:
    return booking_service


def get_otp_service() -> OTPService:
    return otp_service


def get_branches_repo(db: Optional[connection] = Depends(get_db)) -> BranchesRepo:
    return BranchesRepo(db=db)


def get_branch_service(
    branches_repo: BranchesRepo = Depends(get_branches_repo),
) -> BranchService:
    return BranchService(repo=branches_repo)


def get_guests_repo(db: Optional[connection] = Depends(get_db)) -> GuestsRepo:
    return GuestsRepo(db=db)


def get_guest_service(
    guests_repo: GuestsRepo = Depends(get_guests_repo),
) -> GuestService:
    return GuestService(repo=guests_repo)


def get_services_repo(db: Optional[connection] = Depends(get_db)) -> ServicesRepo:
    return ServicesRepo(db=db)


def get_services_service(
    services_repo: ServicesRepo = Depends(get_services_repo),
) -> ServicesService:
    return ServicesService(repo=services_repo)


def get_billing_repo(db: Optional[connection] = Depends(get_db)) -> BillingRepo:
    return BillingRepo(db=db)


def get_billing_service(
    billing_repo: BillingRepo = Depends(get_billing_repo),
) -> BillingService:
    return BillingService(repo=billing_repo)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/public/otp/verify")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/v1/public/otp/verify", auto_error=False)

def get_current_guest(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

def get_current_guest_optional(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    return decode_access_token(token)
