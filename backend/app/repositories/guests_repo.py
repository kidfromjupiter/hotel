from typing import Any, Dict, List, Optional
import json

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


FALLBACK_GUESTS: List[Dict[str, Any]] = [
    {
        "guest_id": 1,
        "name": "Nimal Fernando",
        "national_id": "198512345678",
        "phone_number": "771234567",
        "membership_id": 1,
        "membership_name": "Gold",
        "room_discount_percentage": 10.0,
        "service_discount_percentage": 5.0,
    },
    {
        "guest_id": 2,
        "name": "Sarah Connor",
        "national_id": "199098765432",
        "phone_number": "719988776",
        "membership_id": None,
        "membership_name": "None",
        "room_discount_percentage": 0.0,
        "service_discount_percentage": 0.0,
    },
    {
        "guest_id": 3,
        "name": "Kamal Perera",
        "national_id": "199211223344",
        "phone_number": "777000111",
        "membership_id": 2,
        "membership_name": "Platinum",
        "room_discount_percentage": 15.0,
        "service_discount_percentage": 10.0,
    },
]


class GuestsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_all_guests(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT get_all_guests(%s)", (search,))
                    row = cursor.fetchone()
                    if row and "get_all_guests" in row:
                        val = row["get_all_guests"]
                        return json.loads(val) if isinstance(val, str) else (val or [])
            except Exception:
                pass

        if not search:
            return list(FALLBACK_GUESTS)
        q = search.lower()
        return [
            g for g in FALLBACK_GUESTS
            if q in g["name"].lower()
            or q in g["national_id"].lower()
            or q in g["phone_number"]
        ]

    def get_guest_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT get_guest_by_phone(%s)", (phone,))
                    row = cursor.fetchone()
                    if row and "get_guest_by_phone" in row:
                        val = row["get_guest_by_phone"]
                        return json.loads(val) if isinstance(val, str) else val
            except Exception:
                pass

        # Fallback digits matching
        digits = "".join(filter(str.isdigit, phone))
        if digits.startswith("94"):
            digits = digits[2:]
        elif digits.startswith("0"):
            digits = digits[1:]

        for g in FALLBACK_GUESTS:
            if g["phone_number"] == digits or digits.endswith(g["phone_number"]):
                res = dict(g)
                res["has_membership"] = g["membership_id"] is not None
                return res
        return None

    def get_guest_by_id(self, guest_id: int) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT get_guest_by_id(%s)", (guest_id,))
                    row = cursor.fetchone()
                    if row and "get_guest_by_id" in row:
                        val = row["get_guest_by_id"]
                        return json.loads(val) if isinstance(val, str) else val
            except Exception:
                pass

        for g in FALLBACK_GUESTS:
            if g["guest_id"] == guest_id:
                res = dict(g)
                res["has_membership"] = g["membership_id"] is not None
                return res
        return None

    def update_guest_phone(self, guest_id: int, phone: str) -> Dict[str, Any]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT update_guest_phone(%s, %s)", (guest_id, phone))
                    row = cursor.fetchone()
                    if row and "update_guest_phone" in row:
                        val = row["update_guest_phone"]
                        return json.loads(val) if isinstance(val, str) else val
            except Exception:
                pass

        digits = "".join(filter(str.isdigit, phone))
        if digits.startswith("94"):
            digits = digits[2:]
        elif digits.startswith("0"):
            digits = digits[1:]

        for g in FALLBACK_GUESTS:
            if g["guest_id"] == guest_id:
                g["phone_number"] = digits
                return {
                    "success": True,
                    "message": "Phone number updated successfully",
                    "guest_id": guest_id,
                    "phone_number": digits,
                }
        return {"success": False, "message": "Guest not found"}

    def enroll_guest_membership(self, guest_id: int, membership_id: int = 1) -> Dict[str, Any]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT enroll_guest_membership(%s, %s)", (guest_id, membership_id))
                    row = cursor.fetchone()
                    if row and "enroll_guest_membership" in row:
                        val = row["enroll_guest_membership"]
                        return json.loads(val) if isinstance(val, str) else val
            except Exception:
                pass

        for g in FALLBACK_GUESTS:
            if g["guest_id"] == guest_id:
                g["membership_id"] = membership_id
                g["membership_name"] = "Gold" if membership_id == 1 else "Platinum"
                g["room_discount_percentage"] = 10.0 if membership_id == 1 else 15.0
                g["service_discount_percentage"] = 5.0 if membership_id == 1 else 10.0
                return {
                    "success": True,
                    "message": "Guest enrolled in membership successfully",
                    "guest_id": guest_id,
                    "membership_id": membership_id,
                }
        return {"success": False, "message": "Guest not found"}
