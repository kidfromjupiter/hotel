from datetime import date
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class BookingRepository:
    def __init__(self, db: Optional[connection] = None):
        self.db = db

    def clear(self):
        """No-op kept for test fixture compatibility; real database cleans up via SQL."""
        pass

    # Booking writes remain in database functions; reads return ordinary rows.

    def room_exists(self, branch_id: int, room_number: int) -> bool:
        if self.db is None:
            raise RuntimeError("Database connection is unavailable")
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM room_details "
                "WHERE branch_id = %s AND room_number = %s)",
                (branch_id, room_number),
            )
            return bool(cursor.fetchone()[0])

    def save_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(booking_data)

        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    if "booking_id" not in record or not record["booking_id"]:
                        cursor.execute(
                            "SELECT nextval(pg_get_serial_sequence('booking', 'booking_id')) AS booking_id"
                        )
                        record["booking_id"] = cursor.fetchone()["booking_id"]

                    if "booking_status" not in record:
                        record["booking_status"] = "CONFIRMED"

                    branch_id = record["branch_id"]
                    room_num = record["room_number"]
                    guest_id = record.get("guest_id", 1)
                    guest_name = record.get("guest_name") or record.get("name")
                    if guest_id and guest_name:
                        cursor.execute("UPDATE guests SET name = %s WHERE guest_id = %s", (guest_name, guest_id))
                    raw_status = record.get("booking_status", "CONFIRMED")
                    status_map = {
                        "confirmed": "CONFIRMED",
                        "checked_in": "CHECKED_IN",
                        "checked_out": "CHECKED_OUT",
                        "cancelled": "CANCELLED",
                    }
                    status = status_map.get(str(raw_status).lower(), str(raw_status).upper() if raw_status else "CONFIRMED")



                    start_date = record.get("start_date") or (record.get("checkIn") or "")[:10]
                    end_date = record.get("end_date") or (record.get("checkOut") or "")[:10]
                    adult_count = record.get("adult_count", record.get("adults", 2))
                    children_count = record.get("children_count", record.get("children", 0))
                    grand_total = float(record.get("grand_total", record.get("totalPrice", 0.0)))
                    amount_paid = float(record.get("amount_paid", 0.0))

                    cursor.execute(
                        """
                        SELECT create_booking(
                            %s::BIGINT, %s::SMALLINT, %s::INT, %s::INT, %s::VARCHAR, %s::DATE, %s::DATE, %s::INT, %s::INT, %s::NUMERIC, %s::NUMERIC
                        )
                        """,
                        (
                            record["booking_id"],
                            room_num,
                            branch_id,
                            guest_id,
                            status,
                            start_date or "2026-10-01",
                            end_date or "2026-10-02",
                            adult_count,
                            children_count,
                            grand_total,
                            amount_paid,
                        ),
                    )
                    row = cursor.fetchone()
                    if not row or row.get("create_booking") is None:
                        raise RuntimeError("Database did not return the created booking")
                    saved = row["create_booking"]
            except Exception as e:
                print(f"Exception in save_booking: {e}")
                import traceback
                traceback.print_exc()
                raise

        if self.db is None:
            raise RuntimeError("Database connection is unavailable")
        return saved

    def find_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT bk.booking_id, bk.booking_ref, bk.guest_id, g.name AS guest_name,
                       g.phone_number::TEXT AS guest_phone,
                       (g.membership_id IS NOT NULL) AS is_member,
                       bk.room_number, bk.branch_id, br.branch_name, rd.room_type_id,
                       bk.booking_status, bk.start_date, bk.end_date,
                       bk.checked_in_time, bk.checked_out_time, bk.adult_count,
                       bk.children_count, bs.invoice_id, bs.total_room_charges,
                       bs.total_service_charges, bs.total_tax_amount, bs.grand_total,
                       bs.amount_paid, bs.payment_status AS invoice_status
                FROM booking bk
                LEFT JOIN guests g ON g.guest_id = bk.guest_id
                LEFT JOIN branches br ON br.branch_id = bk.branch_id
                LEFT JOIN room_details rd
                  ON rd.room_number = bk.room_number AND rd.branch_id = bk.branch_id
                LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
                WHERE bk.booking_id = %s
                """,
                (booking_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_service_charges(self, booking_id: int) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT cat.service_name, sc.service_dates, sc.service_total
                FROM service_charges sc
                LEFT JOIN service_catalogue cat ON cat.service_id = sc.service_id
                WHERE sc.booking_id = %s
                ORDER BY sc.service_log_id
                """,
                (booking_id,),
            )
            return list(cursor.fetchall())

    def find_booking_by_ref(self, booking_ref: str) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        with self.db.cursor() as cursor:
            cursor.execute("SELECT booking_id FROM booking WHERE booking_ref = %s", (booking_ref,))
            row = cursor.fetchone()
        return self.find_booking_by_id(row[0]) if row else None

    def list_all_bookings(
        self,
        branch_id: Optional[int] = None,
        guest_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT bk.booking_id, bk.booking_ref, bk.guest_id, g.name AS guest_name,
                       g.phone_number::TEXT AS guest_phone,
                       (g.membership_id IS NOT NULL) AS is_member,
                       bk.room_number, bk.branch_id, br.branch_name, rd.room_type_id,
                       bk.booking_status, bk.start_date, bk.end_date,
                       bk.checked_in_time, bk.checked_out_time, bk.adult_count,
                       bk.children_count, bs.grand_total, bs.amount_paid,
                       bs.payment_status AS invoice_status
                FROM booking bk
                LEFT JOIN guests g ON g.guest_id = bk.guest_id
                LEFT JOIN branches br ON br.branch_id = bk.branch_id
                LEFT JOIN room_details rd
                  ON rd.room_number = bk.room_number AND rd.branch_id = bk.branch_id
                LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
                WHERE (%s::INT IS NULL OR bk.branch_id = %s)
                  AND (%s::INT IS NULL OR bk.guest_id = %s)
                  AND (%s::TEXT IS NULL OR LOWER(bk.booking_status) = LOWER(%s))
                  AND (%s::DATE IS NULL OR bk.start_date >= %s::DATE)
                  AND (%s::DATE IS NULL OR bk.end_date <= %s::DATE)
                ORDER BY bk.booking_id DESC
                """,
                (branch_id, branch_id, guest_id, guest_id, status, status,
                 start_date, start_date, end_date, end_date),
            )
            return list(cursor.fetchall())

    def get_admin_reservations_list(
        self,
        branch_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT bk.booking_id, bk.booking_ref, bk.guest_id, g.name AS guest_name,
                       g.phone_number::TEXT AS guest_contact, bk.room_number,
                       rd.room_type_id, bk.branch_id, br.branch_name,
                       bk.booking_status, bk.start_date, bk.end_date,
                       (bk.end_date - bk.start_date) AS nights,
                       bk.adult_count, bk.children_count,
                       COALESCE(bs.total_room_charges, 0) AS total_room_charges,
                       COALESCE(bs.total_service_charges, 0) AS total_service_charges,
                       COALESCE(bs.total_tax_amount, 0) AS total_tax_amount,
                       COALESCE(bs.grand_total, 0) AS grand_total,
                       COALESCE(bs.amount_paid, 0) AS amount_paid,
                       GREATEST(COALESCE(bs.grand_total, 0) - COALESCE(bs.amount_paid, 0), 0) AS balance_amount,
                       COALESCE(bs.payment_status, 'UNPAID') AS invoice_status,
                       COALESCE(bs.payment_method, 'NONE') AS payment_method
                FROM booking bk
                LEFT JOIN guests g ON g.guest_id = bk.guest_id
                LEFT JOIN branches br ON br.branch_id = bk.branch_id
                LEFT JOIN room_details rd
                  ON rd.room_number = bk.room_number AND rd.branch_id = bk.branch_id
                LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
                WHERE (%s::INT IS NULL OR bk.branch_id = %s)
                  AND (%s::TEXT IS NULL OR %s = '' OR bk.booking_status ILIKE %s)
                ORDER BY bk.booking_id DESC
                """,
                (branch_id, branch_id, status, status, status),
            )
            return list(cursor.fetchall())

    def update_booking(
        self, booking_id: int, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if self.db is None:
            return None
        status = updates.get("booking_status")
        expected_status = {"CHECKED_IN": "CONFIRMED", "CANCELLED": "CONFIRMED"}.get(status)
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE booking
                SET booking_status = %s,
                    checked_in_time = COALESCE(%s::TIME, checked_in_time),
                    checked_out_time = COALESCE(%s::TIME, checked_out_time)
                WHERE booking_id = %s
                  AND (%s::TEXT IS NULL OR booking_status = %s)
                RETURNING booking_id
                """,
                (status, updates.get("checked_in_time"), updates.get("checked_out_time"),
                 booking_id, expected_status, expected_status),
            )
            row = cursor.fetchone()
        return self.find_booking_by_id(row["booking_id"]) if row else None

    def add_service_to_booking(
        self, booking_id: int, service_id: int, service_dates: int
    ) -> None:
        if self.db is None:
            raise RuntimeError("Database connection is unavailable")

        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT add_service_to_booking(%s, %s, %s)",
                (booking_id, service_id, service_dates),
            )

    def extend_stay(
        self, booking_id: int, new_check_out_date: date
    ) -> Dict[str, Any]:
        if self.db is None:
            raise RuntimeError("Database connection is unavailable")

        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT extend_booking_stay(%s, %s)",
                (booking_id, new_check_out_date),
            )
            row = cursor.fetchone()
            if row and row.get("extend_booking_stay") is not None:
                return row["extend_booking_stay"]

        return {
            "success": False,
            "error_code": "UNKNOWN",
            "message": "The stay could not be extended.",
        }
