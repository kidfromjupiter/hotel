from typing import Any, Dict, List, Optional
from decimal import Decimal
from uuid import UUID
import json

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class BillingRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_all_invoices(
        self, payment_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_all_invoices(%s)", (payment_status,))
                row = cursor.fetchone()
                if row and "get_all_invoices" in row:
                    val = row["get_all_invoices"]
                    return json.loads(val) if isinstance(val, str) else (val or [])
        return []

    def get_active_stays(self) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_active_stays()")
                row = cursor.fetchone()
                if row and "get_active_stays" in row:
                    val = row["get_active_stays"]
                    return json.loads(val) if isinstance(val, str) else (val or [])
        return []

    def record_payment(
        self, invoice_id: UUID, amount: Decimal, payment_method: str
    ) -> Dict[str, Any]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT record_invoice_payment(%s, %s, %s)",
                    (str(invoice_id), amount, payment_method),
                )
                row = cursor.fetchone()
                if row and "record_invoice_payment" in row:
                    val = row["record_invoice_payment"]
                    return json.loads(val) if isinstance(val, str) else val
        return {"success": False, "error_code": "NOT_FOUND", "message": "Invoice not found."}

    def checkout_booking(self, booking_id: int) -> Dict[str, Any]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT checkout_booking(%s)",
                    (booking_id,),
                )
                row = cursor.fetchone()
                if row and "checkout_booking" in row:
                    val = row["checkout_booking"]
                    return json.loads(val) if isinstance(val, str) else val

        return {"success": False, "error_code": "NOT_FOUND", "message": "Booking not found"}
