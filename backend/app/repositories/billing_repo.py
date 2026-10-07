from typing import Any, Dict, List, Optional
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

    def checkout_booking(
        self, booking_id: int, payment_method: str = "CREDIT_CARD"
    ) -> Dict[str, Any]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT checkout_booking(%s, %s)",
                    (booking_id, payment_method),
                )
                row = cursor.fetchone()
                if row and "checkout_booking" in row:
                    val = row["checkout_booking"]
                    return json.loads(val) if isinstance(val, str) else val

        return {"success": False, "message": "Booking not found"}
