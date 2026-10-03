from typing import Any, Dict, List, Optional

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

    def checkout(
        self, booking_id: int, payment_method: str = "CREDIT_CARD"
    ) -> Dict[str, Any]:
        return self.repo.checkout_booking(
            booking_id=booking_id,
            payment_method=payment_method,
        )
