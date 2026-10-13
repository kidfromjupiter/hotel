from typing import Any, Dict, List, Optional
from decimal import Decimal
from uuid import UUID

from app.repositories.billing_repo import BillingRepo


class BillingService:
    def __init__(self, repo: BillingRepo) -> None:
        self.repo = repo

    def list_invoices(
        self, payment_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.repo.get_all_invoices(payment_status=payment_status)

    def list_active_stays(self) -> List[Dict[str, Any]]:
        return self.repo.get_active_stays()

    def record_payment(
        self, invoice_id: UUID, amount: Decimal, payment_method: str
    ) -> Dict[str, Any]:
        return self.repo.record_payment(invoice_id, amount, payment_method)

    def checkout(self, booking_id: int) -> Dict[str, Any]:
        return self.repo.checkout_booking(booking_id=booking_id)
