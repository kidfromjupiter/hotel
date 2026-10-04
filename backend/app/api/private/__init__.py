from fastapi import APIRouter

from app.api.private.billing import router as billing_router
from app.api.private.bookings import router as bookings_router
from app.api.private.guests import router as guests_router
from app.api.private.reports import router as reports_router
from app.api.private.services import router as services_router

private_router = APIRouter()

private_router.include_router(
    bookings_router, prefix="/bookings", tags=["Staff - Bookings"]
)
private_router.include_router(
    reports_router, prefix="/reports", tags=["Staff - Reports"]
)
private_router.include_router(
    billing_router, prefix="/billing", tags=["Staff - Billing & Invoices"]
)
private_router.include_router(
    guests_router, prefix="/guests", tags=["Staff - Guests"]
)
private_router.include_router(
    services_router, prefix="/services", tags=["Staff - Services"]
)
