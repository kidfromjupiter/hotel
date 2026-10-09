from datetime import date
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class RoomsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_rooms(
        self, check_in: date, check_out: date, branch: str, children: int, adults: int
    ) -> List[Dict[str, Any]]:
        branch_lower = branch.lower() if branch else "colombo"

        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT get_available_rooms(%s, %s, %s, %s, %s)",
                    (check_in, check_out, branch_lower, children, adults),
                )
                row = cursor.fetchone()
                if row and "get_available_rooms" in row and row["get_available_rooms"] is not None:
                    return row["get_available_rooms"]

        return []

    def get_all_rooms(self) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        rd.room_number, 
                        rd.room_type_id as room_type, 
                        rd.branch_id, 
                        b.branch_name, 
                        rt.daily_rate, 
                        rd.room_status 
                    FROM room_details rd
                    JOIN branches b ON rd.branch_id = b.branch_id
                    JOIN room_types rt ON rd.room_type_id = rt.room_type_id
                    ORDER BY b.branch_id, rd.room_number
                    """
                )
                return cursor.fetchall()
        return []
