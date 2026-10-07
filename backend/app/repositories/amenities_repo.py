from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class AmenitiesRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_amenities_for_branch(self, branch: str) -> List[Dict[str, Any]]:
        branch_lower = branch.lower() if branch else "colombo"

        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_branch_amenities(%s)", (branch_lower,))
                row = cursor.fetchone()
                if row and "get_branch_amenities" in row and row["get_branch_amenities"]:
                    return row["get_branch_amenities"]

        return []
