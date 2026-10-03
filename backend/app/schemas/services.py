from typing import Optional
from pydantic import BaseModel


class ChargeServiceRequest(BaseModel):
    booking_id: int
    service_id: int
    service_dates: Optional[int] = 1


class AddExtraAmenityRequest(BaseModel):
    booking_id: int
    amenity_id: int
    quantity: Optional[int] = 1
