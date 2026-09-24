from fastapi import APIRouter

from app.api.public.amenities import router as amenities_router
from app.api.public.bookings import router as bookings_router
from app.api.public.branches import router as branches_router
from app.api.public.otp import router as otp_router
from app.api.public.rooms import router as rooms_router

public_router = APIRouter()

public_router.include_router(rooms_router, prefix="/rooms", tags=["Public - Rooms"])
public_router.include_router(
    bookings_router, prefix="/bookings", tags=["Public - Bookings"]
)
public_router.include_router(
    amenities_router, prefix="/amenities", tags=["Public - Amenities"]
)
public_router.include_router(otp_router, prefix="/otp", tags=["Public - OTP"])
public_router.include_router(
    branches_router, prefix="/branches", tags=["Public - Branches"]
)
