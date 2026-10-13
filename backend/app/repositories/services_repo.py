from typing import Any, Dict, List, Optional
import json

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class ServicesRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_services(self) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT service_id, service_name, day_rate, description "
                "FROM service_catalogue ORDER BY service_id"
            )
            return list(cursor.fetchall())

    def charge_service(
        self, booking_id: int, service_id: int, service_dates: int = 1
    ) -> Dict[str, Any]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT add_service_to_booking(%s, %s, %s)",
                    (booking_id, service_id, service_dates),
                )
                row = cursor.fetchone()
                if row and "add_service_to_booking" in row:
                    val = row["add_service_to_booking"]
                    return json.loads(val) if isinstance(val, str) else val

        return {"success": False, "message": "Failed to charge service"}
