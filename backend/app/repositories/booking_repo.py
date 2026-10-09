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
                    name_val = record.get("name") or record.get("guest_name")
                    nic_val = record.get("national_id") or record.get("nic")
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
                                    if name_val and nic_val:
                                        cursor.execute("UPDATE guests SET name = %s, national_id = %s WHERE guest_id = %s", (name_val, nic_val, guest_id))
                                    elif name_val:
                                        cursor.execute("UPDATE guests SET name = %s WHERE guest_id = %s", (name_val, guest_id))
                                    elif nic_val:
                                        cursor.execute("UPDATE guests SET national_id = %s WHERE guest_id = %s", (nic_val, guest_id))
                                else:
                                    cursor.execute("SELECT COALESCE(MAX(guest_id), 0) + 1 FROM guests")
                                    new_gid = cursor.fetchone()["?column?"]
                                    cursor.execute(
                                        "INSERT INTO guests (guest_id, name, phone_number, national_id) VALUES (%s, %s, %s, %s)",
                                        (new_gid, name_val or "Guest", int(raw_phone), nic_val),
                                    )
                                    guest_id = new_gid
                        except Exception:
                            pass
                    elif guest_id and (name_val or nic_val):
                        try:
                            if name_val and nic_val:
                                cursor.execute("UPDATE guests SET name = %s, national_id = %s WHERE guest_id = %s", (name_val, nic_val, guest_id))
                            elif name_val:
                                cursor.execute("UPDATE guests SET name = %s WHERE guest_id = %s", (name_val, guest_id))
                            elif nic_val:
                                cursor.execute("UPDATE guests SET national_id = %s WHERE guest_id = %s", (nic_val, guest_id))
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
                    "pricePerNight": 48000,
                    "membershipPrice": 43200,
                    "membershipDiscount": 10,
                    "maxCapacity": 3,
                    "features": [
                        "King Bed",
                        "Ocean View",
                        "Free Minibar",
                        "Rain Shower",
                    ],
                    "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": True,
                },
                {
                    "id": "presidential-suite",
                    "type": "Fortress Grand Villa",
                    "name": "Fortress Grand Villa",
                    "description": "Grand heritage villa with private plunge pool and 24/7 dedicated butler service.",
                    "pricePerNight": 75000,
                    "membershipPrice": 67500,
                    "membershipDiscount": 10,
                    "maxCapacity": 4,
                    "features": [
                        "Private Pool",
                        "Butler Service",
                        "Oceanfront",
                        "Gourmet Kitchen",
                    ],
                    "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
            ]
        else:
            return [
                {
                    "id": "standard-room",
                    "type": "City View Standard",
                    "name": "City View Standard",
                    "description": "Sophisticated urban sanctuary overlooking the shimmering Colombo skyline.",
                    "pricePerNight": 25000,
                    "membershipPrice": 22500,
                    "membershipDiscount": 10,
                    "maxCapacity": 2,
                    "features": [
                        "Queen Bed",
                        "City View",
                        "Ergonomic Workspace",
                        "High-Speed Wi-Fi",
                    ],
                    "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
                {
                    "id": "deluxe-room",
                    "type": "Executive Oceanfront Deluxe",
                    "name": "Executive Oceanfront Deluxe",
                    "description": "Floor-to-ceiling vistas of Galle Face Green and the vibrant Port City sunsets.",
                    "pricePerNight": 35000,
                    "membershipPrice": 31500,
                    "membershipDiscount": 10,
                    "maxCapacity": 3,
                    "features": [
                        "King Bed",
                        "Ocean View",
                        "Lounge Access",
                        "Marble Bathroom",
                    ],
                    "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": True,
                },
                {
                    "id": "presidential-suite",
                    "type": "Skyline Presidential Suite",
                    "name": "Skyline Presidential Suite",
                    "description": "Top-floor sprawling residence offering premier luxury and panoramic ocean views.",
                    "pricePerNight": 65000,
                    "membershipPrice": 58500,
                    "membershipDiscount": 10,
                    "maxCapacity": 4,
                    "features": [
                        "2 King Bedrooms",
                        "Jacuzzi",
                        "Skyline View",
                        "Private Bar",
                    ],
                    "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
            ]

    def get_amenities_catalog(self, branch: str) -> List[Dict[str, Any]]:
        branch_lower = branch.lower() if branch else "colombo"
        if branch_lower == "kandy":
            return [
                {
                    "id": "kandy-tea-tour",
                    "name": "Ceylon Tea Tasting & Estate Walk",
                    "description": "Guided tasting session and scenic walking tour across organic tea estates.",
                    "price": 4500,
                    "icon": "cup",
                },
                {
                    "id": "spa-ayurveda",
                    "name": "Traditional Ayurvedic Spa Therapy",
                    "description": "60-minute rejuvenating herbal massage and steam bath.",
                    "price": 8500,
                    "icon": "spa",
                },
                {
                    "id": "airport-transfer",
                    "name": "Airport Shuttle Transfer",
                    "description": "Comfortable air-conditioned private vehicle transfer.",
                    "price": 12000,
                    "icon": "car",
                },
            ]
        elif branch_lower == "galle":
            return [
                {
                    "id": "sunset-cruise",
                    "name": "Galle Coastal Sunset Cruise",
                    "description": "Private catamaran boat ride with cocktails along the southern coastline.",
                    "price": 9500,
                    "icon": "water",
                },
                {
                    "id": "surf-lesson",
                    "name": "Private Surfing Lesson",
                    "description": "2-hour beginner or intermediate surf session with certified instructor.",
                    "price": 6000,
                    "icon": "waves",
                },
                {
                    "id": "airport-transfer",
                    "name": "Airport Shuttle Transfer",
                    "description": "Direct highway transfer from BIA Airport to Galle.",
                    "price": 14000,
                    "icon": "car",
                },
            ]
        else:
            return [
                {
                    "id": "airport-pickup",
                    "name": "Airport Pickup & Luxury Transfer",
                    "description": "Luxury chauffeur transfer from Bandaranaike International Airport (BIA).",
                    "price": 5000,
                    "icon": "car",
                },
                {
                    "id": "buffet-breakfast",
                    "name": "Gourmet Oceanview Breakfast Buffet",
                    "description": "Daily lavish breakfast spread featuring international and Sri Lankan delicacies.",
                    "price": 3500,
                    "icon": "restaurant",
                },
                {
                    "id": "spa-access",
                    "name": "SkyNest Spa & Hydrotherapy Day Pass",
                    "description": "Full-day access to sauna, steam rooms, and infinity hydro-pool.",
                    "price": 7500,
                    "icon": "spa",
                },
            ]

    def add_service_to_booking(self, booking_id: int, payload):
        b = self.find_booking_by_id(booking_id)
        if b:
            if "service_charges" not in b:
                b["service_charges"] = []
                
            new_service = {
                "service_name": payload.service_name,
                "service_total": payload.service_total,
                "service_dates": payload.service_dates
            }
            b["service_charges"].append(new_service)
            
            # Update grand total
            current_total = b.get("grand_total", 0.0)
            b["grand_total"] = current_total + payload.service_total
            return True
        return False

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
        return [
            {"service_id": 1, "service_name": "Airport Transfer", "day_rate": 5000.0, "description": "Airport Transfer"},
            {"service_id": 2, "service_name": "Laundry", "day_rate": 1500.0, "description": "Laundry"},
            {"service_id": 3, "service_name": "Room Service", "day_rate": 2500.0, "description": "Room Service"},
            {"service_id": 4, "service_name": "Spa", "day_rate": 7500.0, "description": "Spa"},
            {"service_id": 5, "service_name": "Breakfast", "day_rate": 3000.0, "description": "Breakfast"},
            {"service_id": 6, "service_name": "Dinner", "day_rate": 4500.0, "description": "Dinner"},
            {"service_id": 7, "service_name": "Extra Bed", "day_rate": 4000.0, "description": "Extra Bed"},
        ]

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
        return [
            {"tax_id": 1, "tax_name": "VAT", "tax_percentage": 15.0},
            {"tax_id": 2, "tax_name": "Service Tax", "tax_percentage": 5.0},
        ]

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

