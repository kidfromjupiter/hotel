from datetime import date
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class RoomsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_rooms(
        self, check_in: date, check_out: date, branch: Optional[str], children: int, adults: int
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT rd.room_number, rd.branch_id, br.branch_name, rd.room_type_id,
                       rd.room_status, rd.capacity, rt.daily_rate
                FROM room_details rd
                JOIN branches br ON br.branch_id = rd.branch_id
                LEFT JOIN room_types rt ON rt.room_type_id = rd.room_type_id
                WHERE (%s::TEXT IS NULL OR LOWER(br.branch_name) = LOWER(%s))
                  AND rd.capacity >= COALESCE(%s, 0) + COALESCE(%s, 0)
                  AND rd.room_status != 'MAINTENANCE'
                  AND NOT EXISTS (
                    SELECT 1 FROM booking bk
                    WHERE bk.room_number = rd.room_number
                      AND bk.branch_id = rd.branch_id
                      AND bk.booking_status != 'CANCELLED'
                      AND bk.start_date < %s AND bk.end_date > %s
                  )
                ORDER BY rd.room_number
                """,
                (branch, branch, adults, children, check_out, check_in),
            )
            return list(cursor.fetchall())

    def get_all_rooms(self) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT rd.room_number, rd.room_type_id as room_type, rd.branch_id,
                       b.branch_name, rt.daily_rate, rd.room_status
                FROM room_details rd
                JOIN branches b ON rd.branch_id = b.branch_id
                JOIN room_types rt ON rd.room_type_id = rt.room_type_id
                ORDER BY b.branch_id, rd.room_number
                """
            )
            return list(cursor.fetchall())
