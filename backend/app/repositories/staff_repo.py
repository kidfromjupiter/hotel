from typing import Any, Dict, Optional
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class StaffRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch staff member by username (used during login)."""
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT staff_id, branch_id, username, password_hash, full_name, role, is_active, created_at
                    FROM staff
                    WHERE username = %s;
                    """,
                    (username,),
                )
                return cursor.fetchone()
        return None

    def get_by_id(self, staff_id: int) -> Optional[Dict[str, Any]]:
        """Fetch staff member by ID (used to validate token requests)."""
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT staff_id, branch_id, username, password_hash, full_name, role, is_active, created_at
                    FROM staff
                    WHERE staff_id = %s;
                    """,
                    (staff_id,),
                )
                return cursor.fetchone()
        return None
