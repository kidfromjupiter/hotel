"""BookingFlowService has been consolidated into BookingService to eliminate redundant service abstractions."""

from app.services.booking_service import BookingService

# Alias for backward compatibility
BookingFlowService = BookingService

__all__ = ["BookingFlowService"]
