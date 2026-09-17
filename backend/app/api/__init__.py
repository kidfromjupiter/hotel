from fastapi import APIRouter
from app.api.branches import router as branches_router
from app.api.rooms import router as rooms_router
from app.api.guests import router as guests_router
from app.api.bookings import router as bookings_router
from app.api.services import router as services_router
from app.api.billing import router as billing_router
from app.api.reports import router as reports_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(branches_router, prefix="/branches", tags=["Branches"])
api_router.include_router(rooms_router, prefix="/rooms", tags=["Rooms"])
api_router.include_router(guests_router, prefix="/guests", tags=["Guests"])
api_router.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(services_router, prefix="/services", tags=["Services"])
api_router.include_router(billing_router, prefix="/billing", tags=["Billing & Invoices"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
