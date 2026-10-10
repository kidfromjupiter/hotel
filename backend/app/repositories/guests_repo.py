from typing import Any, Dict, List, Optional
import json

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class GuestsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def create_guest(self, phone: str, name: str = "Guest") -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    cursor.execute("SELECT COALESCE(MAX(guest_id), 0) + 1 FROM guests")
                    new_id = cursor.fetchone()[0]
                    
                    v_digits = "".join([c for c in phone if c.isdigit()])
                    if v_digits.startswith("94"):
                        v_digits = v_digits[2:]
                    elif v_digits.startswith("0"):
                        v_digits = v_digits[1:]
                    
                    phone_int = int(v_digits) if v_digits else 0
                    
                    cursor.execute(
                        "INSERT INTO guests (guest_id, name, phone_number) VALUES (%s, %s, %s)",
                        (new_id, name, phone_int)
                    )
                self.db.commit()
                return self.get_guest_by_id(new_id)
            except Exception as e:
                print(f"Failed to create guest: {e}")
                pass
        return None

    def get_all_guests(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_all_guests(%s)", (search,))
                row = cursor.fetchone()
                if row and "get_all_guests" in row:
                    val = row["get_all_guests"]
                    return json.loads(val) if isinstance(val, str) else (val or [])
        return []

    def get_guest_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_guest_by_phone(%s)", (phone,))
                row = cursor.fetchone()
                if row and "get_guest_by_phone" in row:
                    val = row["get_guest_by_phone"]
                    return json.loads(val) if isinstance(val, str) else val
        return None

    def get_guest_by_id(self, guest_id: int) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_guest_by_id(%s)", (guest_id,))
                row = cursor.fetchone()
                if row and "get_guest_by_id" in row:
                    val = row["get_guest_by_id"]
                    return json.loads(val) if isinstance(val, str) else val
        return None

    def update_guest_phone(self, guest_id: int, phone: str) -> Dict[str, Any]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT update_guest_phone(%s, %s)", (guest_id, phone))
                row = cursor.fetchone()
                if row and "update_guest_phone" in row:
                    val = row["update_guest_phone"]
                    return json.loads(val) if isinstance(val, str) else val
        return {"success": False, "message": "Guest not found"}

    def enroll_guest_membership(self, guest_id: int, membership_id: int = 1) -> Dict[str, Any]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT enroll_guest_membership(%s, %s)", (guest_id, membership_id))
                row = cursor.fetchone()
                if row and "enroll_guest_membership" in row:
                    val = row["enroll_guest_membership"]
                    return json.loads(val) if isinstance(val, str) else val
        return {"success": False, "message": "Guest not found"}

    def enroll_by_phone(self, name: str, phone: str) -> Dict[str, Any]:
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Look up guest
                    cursor.execute("SELECT guest_id FROM guests WHERE phone_number = %s", (phone,))
                    row = cursor.fetchone()
                    
                    if row:
                        guest_id = row['guest_id']
                        # Set membership_id = 1
                        cursor.execute("UPDATE guests SET membership_id = 1 WHERE guest_id = %s", (guest_id,))
                    else:
                        # Create new guest with membership
                        cursor.execute(
                            "INSERT INTO guests (guest_id, membership_id, name, national_id, phone_number) VALUES ((SELECT COALESCE(MAX(guest_id),0)+1 FROM guests), 1, %s, 'PENDING', %s)",
                            (name, phone)
                        )
                    return {"success": True, "message": f"Successfully enrolled {name} in SkyNest Membership!"}
            except Exception as e:
                print(f"Database error in enroll_by_phone: {e}")
                return {"success": False, "message": "Database error enrolling member."}
        return {"success": True, "message": "In-memory success."}
