from typing import Any, Dict, List, Optional
from decimal import Decimal
from uuid import UUID
from fastapi.encoders import jsonable_encoder

from app.repositories.billing_repo import BillingRepo


class BillingService:
    def __init__(self, repo: BillingRepo) -> None:
        self.repo = repo

    def list_invoices(
        self, payment_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return jsonable_encoder([
            {**row, "guest_name": row.get("guest_name") or "Valued Guest",
             "guest_phone": row.get("guest_phone") or "",
             "branch_name": row.get("branch_name") or "Main Branch",
             "payment_method": row.get("payment_method") or "CREDIT_CARD",
             "total_service_charges": row.get("total_service_charges") or 0,
             "total_tax_amount": row.get("total_tax_amount") or 0}
            for row in self.repo.get_all_invoices(payment_status=payment_status)
        ])

    def list_active_stays(self) -> List[Dict[str, Any]]:
        return jsonable_encoder([
            {**row, "guest_name": row.get("guest_name") or "Valued Guest",
             "guest_phone": row.get("guest_phone") or "",
             "room_type_id": row.get("room_type_id") or "Standard",
             "membership_name": row.get("membership_name") or "None",
             "room_discount_percentage": row.get("room_discount_percentage") or 0,
             "service_discount_percentage": row.get("service_discount_percentage") or 0}
            for row in self.repo.get_active_stays()
        ])

    def record_payment(
        self, invoice_id: UUID, amount: Decimal, payment_method: str
    ) -> Dict[str, Any]:
        return self.repo.record_payment(invoice_id, amount, payment_method)

    def checkout(self, booking_id: int) -> Dict[str, Any]:
        return self.repo.checkout_booking(booking_id=booking_id)
