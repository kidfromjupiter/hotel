from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from psycopg2.extensions import connection

from app.core.security import decode_access_token


from app.db import get_db
from app.repositories.amenities_repo import AmenitiesRepo
from app.repositories.billing_repo import BillingRepo
from app.repositories.booking_repo import BookingRepository
from app.repositories.branches_repo import BranchesRepo
from app.repositories.guests_repo import GuestsRepo
from app.repositories.reports_repo import ReportsRepo
from app.repositories.rooms_repo import RoomsRepo
from app.repositories.services_repo import ServicesRepo
from app.services.amenities_service import AmenitiesService
from app.services.billing_service import BillingService
from app.services.booking_service import BookingService
from app.services.branch_service import BranchService
from app.services.guest_service import GuestService
from app.services.otp_service import OTPService
from app.services.report_service import ReportService
from app.services.room_service import RoomService
from app.services.services_service import ServicesService
from app.config import get_settings
from app.config import get_settings
from app.schemas.auth import StaffUser
from app.repositories.staff_repo import StaffRepo
from app.services.auth_service import AuthService


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


def get_amenities_repo(db: Optional[connection] = Depends(get_db)) -> AmenitiesRepo:
    return AmenitiesRepo(db=db)


def get_amenities_service(
    amenities_repo: AmenitiesRepo = Depends(get_amenities_repo),
) -> AmenitiesService:
    return AmenitiesService(repo=amenities_repo)


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

def get_staff_repo(db: Optional[connection] = Depends(get_db)) -> StaffRepo:
    return StaffRepo(db=db)


def get_auth_service(
    staff_repo: StaffRepo = Depends(get_staff_repo),
) -> AuthService:
    settings = get_settings()
    return AuthService(
        repo=staff_repo,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

# HTTPBearer adds the "Authorize" button and Bearer token parsing
http_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    auth_service: AuthService = Depends(get_auth_service),
    staff_repo: StaffRepo = Depends(get_staff_repo),
) -> StaffUser:
    """
    Extracts Bearer token from header, verifies signature,
    and returns the active StaffUser object.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    staff_id = payload.get("staff_id")
    if not staff_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = staff_repo.get_by_id(int(staff_id))
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or no longer exists.",
        )

    return StaffUser(
        staff_id=user["staff_id"],
        branch_id=user.get("branch_id"),
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=user["is_active"],
    )


def require_admin(
    current_user: StaffUser = Depends(get_current_user),
) -> StaffUser:
    """Ensures only staff with the 'admin' role can access the endpoint."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Administrator privileges required.",
        )
    return current_user


def enforce_branch_access(
    requested_branch_id: Optional[int],
    current_user: StaffUser,
) -> Optional[int]:
    """
    Branch scoping rule:
    - Admin: can view all branches (None) or filter by any branch.
    - Receptionist: strictly restricted to their own assigned branch.
    """
    if current_user.role == "admin":
        return requested_branch_id

    # For receptionists:
    if requested_branch_id is not None and requested_branch_id != current_user.branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You only have access to branch {current_user.branch_id}.",
        )
    return current_user.branch_id

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
