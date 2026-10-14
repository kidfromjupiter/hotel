from typing import Any, Dict, List, Optional, Tuple

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

from app.phone import normalize_phone


GUEST_COLUMNS = """
    g.guest_id, g.name, g.national_id, g.phone_number::TEXT AS phone_number,
    g.membership_id, (g.membership_id IS NOT NULL) AS has_membership,
    COALESCE(m.membership_name, 'None') AS membership_name,
    COALESCE(m.room_discount_percentage, 0) AS room_discount_percentage,
    COALESCE(m.service_discount_percentage, 0) AS service_discount_percentage
"""


class GuestsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def create_guest(self, phone: str, name: str = "Guest") -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        normalized = normalize_phone(phone)
        if normalized is None:
            return None
        with self.db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO guests (name, phone_number) VALUES (%s, %s) RETURNING guest_id",
                (name, normalized),
            )
            guest_id = cursor.fetchone()[0]
        return self.get_guest_by_id(guest_id)

    def get_all_guests(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"""
                SELECT {GUEST_COLUMNS}
                FROM guests g
                LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
                WHERE (%s::TEXT IS NULL OR g.name ILIKE '%%' || %s || '%%'
                    OR g.national_id ILIKE '%%' || %s || '%%'
                    OR g.phone_number::TEXT ILIKE '%%' || %s || '%%')
                ORDER BY g.guest_id
                """,
                (search, search, search, search),
            )
            return list(cursor.fetchall())

    def get_guest_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        normalized = normalize_phone(phone)
        if normalized is None:
            return None
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"""
                SELECT {GUEST_COLUMNS}
                FROM guests g
                LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
                WHERE g.phone_number = %s
                LIMIT 1
                """,
                (normalized,),
            )
            return cursor.fetchone()

    def get_guest_by_id(self, guest_id: int) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"""
                SELECT {GUEST_COLUMNS}
                FROM guests g
                LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
                WHERE g.guest_id = %s
                """,
                (guest_id,),
            )
            return cursor.fetchone()

    def get_payment_history_rows(
        self, query: str, branch_id: Optional[int] = None
    ) -> Optional[Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]]:
        if self.db is None or not query.strip():
            return None
        lookup = query.strip()
        normalized = normalize_phone(lookup)
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT guest_id, name, phone_number::TEXT AS phone_number "
                "FROM guests WHERE guest_id::TEXT = %s LIMIT 1",
                (lookup,),
            )
            guest = cursor.fetchone()
            if guest is None and normalized:
                cursor.execute(
                    "SELECT guest_id, name, phone_number::TEXT AS phone_number "
                    "FROM guests WHERE phone_number::TEXT = %s LIMIT 1",
                    (normalized,),
                )
                guest = cursor.fetchone()
            if guest is None:
                return None
            guest_id = guest["guest_id"]
            cursor.execute(
                """
                SELECT COUNT(bk.booking_id) AS booking_count,
                       COALESCE(SUM(COALESCE(bs.grand_total, 0)), 0) AS grand_total,
                       COALESCE(SUM(COALESCE(bs.amount_paid, 0)), 0) AS amount_paid,
                       COALESCE(SUM(GREATEST(0, COALESCE(bs.grand_total, 0) - COALESCE(bs.amount_paid, 0))), 0) AS outstanding_balance
                FROM booking bk
                LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
                WHERE bk.guest_id = %s AND (%s::INT IS NULL OR bk.branch_id = %s)
                """,
                (guest_id, branch_id, branch_id),
            )
            summary = cursor.fetchone()
            cursor.execute(
                """
                SELECT bk.booking_id, bk.booking_ref, bk.branch_id, br.branch_name,
                       bk.start_date, bk.end_date, bk.booking_status, bs.invoice_id,
                       COALESCE(bs.payment_method, 'NONE') AS payment_method,
                       COALESCE(bs.payment_status, 'UNPAID') AS payment_status,
                       COALESCE(bs.grand_total, 0) AS grand_total,
                       COALESCE(bs.amount_paid, 0) AS amount_paid,
                       GREATEST(0, COALESCE(bs.grand_total, 0) - COALESCE(bs.amount_paid, 0)) AS outstanding_balance
                FROM booking bk
                LEFT JOIN branches br ON br.branch_id = bk.branch_id
                LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
                WHERE bk.guest_id = %s AND (%s::INT IS NULL OR bk.branch_id = %s)
                ORDER BY bk.start_date DESC, bk.booking_id DESC
                """,
                (guest_id, branch_id, branch_id),
            )
            return dict(guest), dict(summary), list(cursor.fetchall())

    def update_guest_phone(self, guest_id: int, phone_number: str) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        normalized = normalize_phone(phone_number)
        if normalized is None:
            return None
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "UPDATE guests SET phone_number = %s WHERE guest_id = %s "
                "RETURNING guest_id, phone_number::TEXT AS phone_number",
                (normalized, guest_id),
            )
            return cursor.fetchone()

    def enroll_guest_membership(self, guest_id: int, membership_id: int = 1) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "UPDATE guests SET membership_id = %s WHERE guest_id = %s "
                "RETURNING guest_id, membership_id",
                (membership_id, guest_id),
            )
            return cursor.fetchone()
