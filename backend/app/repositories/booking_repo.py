import random
import string
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

    def generate_booking_ref(self) -> str:
        random_code = "".join(random.choices(string.digits, k=4))
        return f"SKN-{random_code}"

    # ── Database-Backed Availability ──

    def get_available_rooms(
        self,
        check_in: date,
        check_out: date,
        branch: str,
        children: int,
        adults: int,
    ) -> List[Dict[str, Any]]:
        branch_clean = branch.lower() if branch else "colombo"

        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT get_available_rooms(%s, %s, %s, %s, %s)",
                        (check_in, check_out, branch_clean, children, adults),
                    )
                    row = cursor.fetchone()
                    if row and "get_available_rooms" in row and row["get_available_rooms"] is not None:
                        rooms = row["get_available_rooms"]
                        if isinstance(rooms, list):
                            return rooms
            except Exception as e:
                print(f"Error in get_available_rooms: {e}")

        return []

    # ── Database-Backed Booking Operations ──

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
                        
                    if "bookingRef" not in record or not record["bookingRef"]:
                        record["bookingRef"] = self.generate_booking_ref()
                    if "booking_status" not in record:
                        record["booking_status"] = "CONFIRMED"

                    branch_map = {"colombo": 1, "kandy": 2, "galle": 3}
                    branch_val = record.get("branch", "colombo")
                    branch_id = branch_map.get(str(branch_val).lower(), record.get("branch_id", 1))

                    room_num = record.get("room_number", 101)
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
                self.db.commit()
            except Exception as e:
                print(f"Exception in save_booking: {e}")
                import traceback
                traceback.print_exc()
                if self.db:
                    self.db.rollback()


        return record

    def find_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT get_booking_by_id(%s)", (booking_id,))
                    row = cursor.fetchone()
                    if row and "get_booking_by_id" in row and row["get_booking_by_id"] is not None:
                        return row["get_booking_by_id"]
            except Exception:
                pass
        return None

    def list_all_bookings(
        self,
        branch_id: Optional[int] = None,
        guest_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT get_all_bookings(%s, %s, %s, %s, %s)",
                        (branch_id, guest_id, status, start_date, end_date),
                    )
                    row = cursor.fetchone()
                    if row and "get_all_bookings" in row and row["get_all_bookings"] is not None:
                        return row["get_all_bookings"]
            except Exception:
                pass
        return []

    def get_admin_reservations_list(
        self,
        branch_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT get_admin_reservations(%s, %s)",
                        (branch_id, status),
                    )
                    row = cursor.fetchone()
                    if row and "get_admin_reservations" in row and row["get_admin_reservations"] is not None:
                        return row["get_admin_reservations"]
            except Exception as e:
                print(f"Error fetching admin reservations: {e}")
        return []

    def update_booking(
        self, booking_id: int, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    status = updates.get("booking_status")
                    check_in_time = updates.get("checked_in_time")
                    check_out_time = updates.get("checked_out_time")
                    cursor.execute(
                        "SELECT update_booking_status(%s, %s, %s, %s)",
                        (booking_id, status, check_in_time, check_out_time),
                    )
                    row = cursor.fetchone()
                    if row and "update_booking_status" in row and row["update_booking_status"] is not None:
                        return row["update_booking_status"]
            except Exception:
                pass
        return None
