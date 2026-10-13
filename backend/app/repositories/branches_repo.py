from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class BranchesRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_branches(self) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT branch_id, branch_name FROM branches ORDER BY branch_id")
            return list(cursor.fetchall())
