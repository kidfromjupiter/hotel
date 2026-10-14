from pydantic import BaseModel, Field


class ChargeServiceRequest(BaseModel):
    booking_id: int
    service_id: int
    quantity: int = Field(default=1, gt=0)
