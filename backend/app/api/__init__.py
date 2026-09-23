from fastapi import APIRouter

from app.api.private import private_router
from app.api.public import public_router

api_router = APIRouter(prefix="/api/v1")

# Two-layer architecture: Public (customer-facing) and Private (staff/internal)
api_router.include_router(public_router, prefix="/public")
api_router.include_router(private_router, prefix="/private")

# Aliases for backward compatibility with existing tests and clients
api_router.include_router(public_router)
api_router.include_router(private_router)
