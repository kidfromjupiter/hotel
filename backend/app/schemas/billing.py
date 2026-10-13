from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    booking_id: int


class RecordPaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    payment_method: Literal["Cash", "Card"]
