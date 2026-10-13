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
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT bs.invoice_id, bs.booking_id, b.booking_ref, g.name AS guest_name,
                       g.phone_number::TEXT AS guest_phone, b.branch_id, br.branch_name,
                       b.room_number, bs.payment_method, bs.total_room_charges,
                       bs.total_service_charges, bs.total_tax_amount, bs.grand_total,
                       bs.amount_paid, bs.payment_status,
                       (bs.grand_total - bs.amount_paid) AS outstanding_balance
                FROM billing_summary bs
                JOIN booking b ON b.booking_id = bs.booking_id
                LEFT JOIN guests g ON g.guest_id = b.guest_id
                LEFT JOIN branches br ON br.branch_id = b.branch_id
                WHERE (%s::TEXT IS NULL OR bs.payment_status ILIKE %s)
                ORDER BY bs.booking_id DESC
                """,
                (payment_status, payment_status),
            )
            return list(cursor.fetchall())

    def get_active_stays(self) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT b.booking_id, b.booking_ref, b.guest_id, g.name AS guest_name,
                       g.phone_number::TEXT AS guest_phone, b.room_number, b.branch_id,
                       rd.room_type_id, b.start_date, b.end_date, b.booking_status,
                       (g.membership_id IS NOT NULL) AS is_member, m.membership_name,
                       m.room_discount_percentage, m.service_discount_percentage
                FROM booking b
                LEFT JOIN guests g ON g.guest_id = b.guest_id
                LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
                LEFT JOIN room_details rd ON rd.room_number = b.room_number AND rd.branch_id = b.branch_id
                WHERE b.booking_status ILIKE '%%check%%' OR b.booking_status ILIKE '%%confirm%%'
                ORDER BY b.start_date
                """
            )
            return list(cursor.fetchall())

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
