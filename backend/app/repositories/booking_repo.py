import random
import string
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class BookingRepository:
    _shared_bookings: List[Dict[str, Any]] = []
    _shared_next_id: int = 500001

    def __init__(self, db: Optional[connection] = None):
        self.db = db
        # Reference shared store for test & offline fallback consistency
        self._bookings: List[Dict[str, Any]] = BookingRepository._shared_bookings

    def clear(self):
        BookingRepository._shared_bookings.clear()

    @property
    def _next_id(self) -> int:
        return BookingRepository._shared_next_id

    @_next_id.setter
    def _next_id(self, val: int):
        BookingRepository._shared_next_id = val

    def generate_booking_ref(self) -> str:
        random_code = "".join(random.choices(string.digits, k=4))
        return f"SKN-{random_code}"

    # ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ Database-Backed Availability ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬

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
            except Exception:
                pass

        # In-memory fallback if DB is not available
        total_guests = adults + children
        all_rooms = self.get_rooms_catalog(branch_clean)
        check_in_str = check_in.isoformat() if isinstance(check_in, (date, datetime)) else str(check_in)
        check_out_str = check_out.isoformat() if isinstance(check_out, (date, datetime)) else str(check_out)

        available_rooms = []
        for room in all_rooms:
            if room.get("maxCapacity", 2) < total_guests:
                continue
            if self.is_room_booked(room["id"], check_in_str, check_out_str):
                continue
            available_rooms.append(room)
        return available_rooms

    
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

                    room_num = record.get("room_number", 101)
                    guest_id = record.get("guest_id", 1)
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
                self.db.commit()
            except Exception as e:
                print(f"Exception in save_booking: {e}")
                import traceback
                traceback.print_exc()
                if self.db:
                    self.db.rollback()
        else:
            if "booking_id" not in record or not record["booking_id"]:
                record["booking_id"] = BookingRepository._shared_next_id
                BookingRepository._shared_next_id += 1
            if "bookingRef" not in record or not record["bookingRef"]:
                record["bookingRef"] = self.generate_booking_ref()
            if "booking_status" not in record:
                record["booking_status"] = "Confirmed"

        # Update in-memory record list
        self._bookings.append(record)
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

        for b in self._bookings:
            if b.get("booking_id") == booking_id:
                return b
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

        # In-memory filtered list
        results = []
        for b in self._bookings:
            if branch_id is not None and b.get("branch_id") != branch_id:
                continue
            if guest_id is not None and b.get("guest_id") != guest_id:
                continue
            if (
                status is not None
                and b.get("booking_status", "").lower() != status.lower()
            ):
                continue
            if start_date is not None and (b.get("start_date") or "") < start_date:
                continue
            if end_date is not None and (b.get("end_date") or "") > end_date:
                continue
            results.append(b)
        return results

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
                        updated_db = row["update_booking_status"]
                        # Also sync in-memory record
                        for b in self._bookings:
                            if b.get("booking_id") == booking_id:
                                b.update(updates)
                                break
                        return updated_db
            except Exception:
                pass

        booking = self.find_booking_by_id(booking_id)
        if booking:
            booking.update(updates)
            return booking
        return None

    def is_overlapping(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        d_start1 = start1[:10]
        d_end1 = end1[:10]
        d_start2 = start2[:10]
        d_end2 = end2[:10]
        return max(d_start1, d_start2) < min(d_end1, d_end2)

    def is_room_booked(self, room_id: str, start_date: str, end_date: str) -> bool:
        for b in self._bookings:
            b_room = b.get("roomId") or str(b.get("room_number"))
            if b_room == room_id:
                b_start = b.get("start_date") or b.get("checkIn") or ""
                b_end = b.get("end_date") or b.get("checkOut") or ""
                if (
                    b_start
                    and b_end
                    and self.is_overlapping(b_start, b_end, start_date, end_date)
                ):
                    return True
        return False

    def get_rooms_catalog(self, branch: str) -> List[Dict[str, Any]]:
        branch_lower = branch.lower() if branch else "colombo"
        if branch_lower == "kandy":
            return [
                {
                    "id": "standard-room",
                    "type": "Standard Mountain View",
                    "name": "Standard Mountain View",
                    "description": "Charming room with scenic hillside views of the Knuckles mountain range.",
                    "pricePerNight": 25000,
                    "membershipPrice": 22500,
                    "membershipDiscount": 10,
                    "maxCapacity": 2,
                    "features": [
                        "Queen Bed",
                        "Mountain View",
                        "Tea Station",
                        "Free Wi-Fi",
                    ],
                    "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
                {
                    "id": "deluxe-room",
                    "type": "Deluxe Plantation Suite",
                    "name": "Deluxe Plantation Suite",
                    "description": "Luxurious suite nestled among tea gardens with a private terrace and colonial charm.",
                    "pricePerNight": 42000,
                    "membershipPrice": 37800,
                    "membershipDiscount": 10,
                    "maxCapacity": 3,
                    "features": [
                        "King Bed",
                        "Private Terrace",
                        "Fireplace",
                        "En-suite Bath",
                    ],
                    "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": True,
                },
                {
                    "id": "family-suite",
                    "type": "Royal Hills Family Suite",
                    "name": "Royal Hills Family Suite",
                    "description": "Spacious two-bedroom retreat ideal for families visiting historic Kandy.",
                    "pricePerNight": 58000,
                    "membershipPrice": 52200,
                    "membershipDiscount": 10,
                    "maxCapacity": 4,
                    "features": [
                        "2 King Beds",
                        "Balcony",
                        "Separate Living Area",
                        "Breakfast Included",
                    ],
                    "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
            ]
        elif branch_lower == "galle":
            return [
                {
                    "id": "standard-room",
                    "type": "Standard Coastal Haven",
                    "name": "Standard Coastal Haven",
                    "description": "Bright and airy coastal room steps away from the historic ramparts of Galle Fort.",
                    "pricePerNight": 28000,
                    "membershipPrice": 25200,
                    "membershipDiscount": 10,
                    "maxCapacity": 2,
                    "features": [
                        "Queen Bed",
                        "Sea Breeze Balcony",
                        "Mini Bar",
                        "Free Wi-Fi",
                    ],
                    "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
                {
                    "id": "deluxe-room",
                    "type": "Oceanview Deluxe Suite",
                    "name": "Oceanview Deluxe Suite",
                    "description": "Uninterrupted panoramas of the Indian Ocean with private sunrise patio.",
    def add_service_to_booking(self, booking_id: int, payload):
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    # 1. Update the grand total in billing_summary
                    cursor.execute(
                        "UPDATE billing_summary SET total_service_charges = COALESCE(total_service_charges, 0) + %s, grand_total = COALESCE(grand_total, 0) + %s WHERE booking_id = %s",
                        (payload.service_total, payload.service_total, booking_id)
                    )
                    
                    # 2. Insert into service_charges (Finds service_id using service_name automatically!)
                    cursor.execute(
                        "
                        INSERT INTO service_charges (service_log_id, booking_id, service_id, service_dates, service_total)
                        SELECT 
                            (SELECT COALESCE(MAX(service_log_id), 0) + 1 FROM service_charges), 
                            %s, 
                            service_id, 
                            %s, 
                            %s 
                        FROM service_catalogue 
                        WHERE service_name = %s
                        ",
                        (booking_id, payload.service_dates, payload.service_total, payload.service_name)
                    )
            except Exception as e:
                print(f"Database error in add_service: {e}")
                pass
                
        # In-memory fallback if the database is offline
        for b in self._bookings:
            if b.get("booking_id") == booking_id:
                if "service_charges" not in b:
                    b["service_charges"] = []
                b["service_charges"].append({
                    "service_name": payload.service_name,
                    "service_total": payload.service_total,
                    "service_dates": payload.service_dates
                })
                b["grand_total"] = b.get("grand_total", 0.0) + payload.service_total
                break

    def find_pending_booking_by_phone(self, phone: str):
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT b.booking_id, g.name AS guest_name, g.phone_number as guest_phone, b.room_number, r.room_type_id, b.booking_status, b.start_date, b.end_date FROM booking b JOIN guests g ON b.guest_id = g.guest_id JOIN room_details r ON b.room_number = r.room_number AND b.branch_id = r.branch_id WHERE g.phone_number = %s AND b.booking_status = 'Confirmed'",
                        (phone,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return row
            except Exception as e:
                print(f"Database error finding pending booking: {e}")
                pass

        # In-memory fallback if the database is offline
        for b in self._bookings:
            guest_phone = b.get("guest_phone", b.get("phone", ""))
            if str(guest_phone) == str(phone) and b.get("booking_status", "Confirmed") == "Confirmed":
                return b
        return None

    def extending_stay(self, booking_id: int, new_checkout_date: str):
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    cursor.execute(
                        "UPDATE booking SET end_date=%s WHERE booking_id=%s",
                        (new_checkout_date, booking_id)
                    )
            except Exception as e:
                print(f"Database error in extending_stay: {e}")
                pass
                
        # In-memory fallback if the database is offline
        for b in self._bookings:
            if b.get("booking_id") == booking_id:
                b["end_date"] = new_checkout_date
                b["checkOut"] = new_checkout_date 
                break