from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class BranchesRepo:
    def __init__(self, db: connection) -> None:
        self.db = db

    def get_all_branches(self):
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT branch_id, branch_name FROM branches"
            )
            return cursor.fetchall()
