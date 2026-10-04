from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class BranchesRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_branches(self) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT get_all_branches()")
                row = cursor.fetchone()
                if row and "get_all_branches" in row:
                    return row["get_all_branches"]
        return []
