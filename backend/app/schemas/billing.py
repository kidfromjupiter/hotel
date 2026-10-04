from typing import Optional
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    booking_id: int
    payment_method: Optional[str] = "CREDIT_CARD"
