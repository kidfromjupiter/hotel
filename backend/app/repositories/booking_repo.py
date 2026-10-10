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
                        cursor.execute("SELECT COALESCE(MAX(booking_id), 0) + 1 FROM booking")
                        record["booking_id"] = cursor.fetchone()["?column?"]

                    if "bookingRef" not in record or not record["bookingRef"]:
                        record["bookingRef"] = self.generate_booking_ref()
                    if "booking_status" not in record:
                        record["booking_status"] = "Confirmed"

                    branch_map = {"colombo": 1, "kandy": 2, "galle": 3}
                    branch_val = record.get("branch", "colombo")
                    branch_id = branch_map.get(str(branch_val).lower(), record.get("branch_id", 1))

                    room_num = record.get("room_number")
                    if not room_num and "roomId" in record:
                        try:
                            room_num = int(str(record["roomId"]).replace("room-", ""))
                        except Exception:
                            room_num = 101
                    if not room_num:
                        room_num = 101

                    guest_id = record.get("guest_id")
                    first_val = record.get("first_name") or record.get("firstName") or ""
                    last_val = record.get("last_name") or record.get("lastName") or ""
                    comb_name = f"{first_val} {last_val}".strip() if (first_val or last_val) else None
                    name_val = comb_name or record.get("name") or record.get("guest_name")
                    nic_val = record.get("national_id") or record.get("nic")
                    email_val = record.get("email")
                    special_requests_val = record.get("special_requests") or record.get("specialRequests")

                    def _update_guest_row(gid: int):
                        updates = []
                        params = []
                        if name_val:
                            updates.append("name = %s")
                            params.append(name_val)
                        if nic_val:
                            updates.append("national_id = %s")
                            params.append(nic_val)
                        if email_val:
                            updates.append("email = %s")
                            params.append(email_val)
                        if updates:
                            params.append(gid)
                            cursor.execute(f"UPDATE guests SET {', '.join(updates)} WHERE guest_id = %s", tuple(params))

                    if not guest_id and record.get("phone"):
                        try:
                            raw_phone = str(record["phone"]).replace("+94", "").replace(" ", "").strip()
                            if raw_phone.startswith("0"):
                                raw_phone = raw_phone[1:]
                            if raw_phone.isdigit():
                                cursor.execute("SELECT guest_id FROM guests WHERE phone_number = %s LIMIT 1", (int(raw_phone),))
                                grow = cursor.fetchone()
                                if grow and grow.get("guest_id"):
                                    guest_id = grow["guest_id"]
                                    _update_guest_row(guest_id)
                                else:
                                    cursor.execute("SELECT COALESCE(MAX(guest_id), 0) + 1 FROM guests")
                                    new_gid = cursor.fetchone()["?column?"]
                                    cursor.execute(
                                        "INSERT INTO guests (guest_id, name, phone_number, national_id, email) VALUES (%s, %s, %s, %s, %s)",
                                        (new_gid, name_val or "Guest", int(raw_phone), nic_val, email_val),
                                    )
                                    guest_id = new_gid
                        except Exception:
                            pass
                    elif guest_id and (name_val or nic_val or email_val):
                        try:
                            _update_guest_row(guest_id)
                        except Exception:
                            pass
                    if not guest_id:
                        guest_id = 1

                    status = record.get("booking_status", "Confirmed")

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

                    if special_requests_val:
                        cursor.execute(
                            "UPDATE booking SET special_requests = %s WHERE booking_id = %s",
                            (special_requests_val, record["booking_id"]),
                        )
                        record["special_requests"] = special_requests_val
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

    def get_service_catalog(self) -> List[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT service_id, service_name, day_rate, description FROM service_catalogue ORDER BY service_id"
                    )
                    rows = cursor.fetchall()
                    if rows:
                        return [dict(r) for r in rows]
            except Exception:
                pass
        return []

    def get_active_tax_policies(self) -> List[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT tax_id, tax_name, tax_percentage FROM tax_policies WHERE active = true ORDER BY tax_id"
                    )
                    rows = cursor.fetchall()
                    if rows:
                        return [dict(r) for r in rows]
            except Exception:
                pass
        return []

    def get_guest_membership_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        if not phone:
            return None
        raw_phone = str(phone).replace("+94", "").replace(" ", "").strip()
        if raw_phone.startswith("0"):
            raw_phone = raw_phone[1:]
        if not raw_phone.isdigit():
            return None
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT g.guest_id, g.name, m.membership_name, m.room_discount_percentage, m.service_discount_percentage
                        FROM guests g
                        LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
                        WHERE g.phone_number = %s
                        LIMIT 1
                        """,
                        (int(raw_phone),),
                    )
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
            except Exception:
                pass
        return None

    def get_booking_summary_for_calculation(self, booking_id: int) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT b.booking_id, b.room_number, b.branch_id, b.start_date, b.end_date,
                               b.adult_count, b.children_count, rd.room_type_id, rt.daily_rate,
                               g.phone_number, m.room_discount_percentage, m.service_discount_percentage
                        FROM booking b
                        LEFT JOIN room_details rd ON b.room_number = rd.room_number AND b.branch_id = rd.branch_id
                        LEFT JOIN room_types rt ON rd.room_type_id = rt.room_type_id
                        LEFT JOIN guests g ON b.guest_id = g.guest_id
                        LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
                        WHERE b.booking_id = %s
                        LIMIT 1
                        """,
                        (booking_id,),
                    )
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
            except Exception:
                pass
        return None
