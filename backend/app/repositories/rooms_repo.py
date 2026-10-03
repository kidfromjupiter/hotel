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
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT get_available_rooms(%s, %s, %s, %s, %s)",
                        (check_in, check_out, branch_lower, children, adults),
                    )
                    row = cursor.fetchone()
                    if row and "get_available_rooms" in row and row["get_available_rooms"] is not None:
                        return row["get_available_rooms"]
            except Exception:
                pass

        return []
