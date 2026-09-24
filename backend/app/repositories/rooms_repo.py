from datetime import date

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class RoomsRepo:
    def __init__(self, db: connection) -> None:
        self.db = db

    def get_rooms(
        self, check_in: date, check_out: date, branch: str, children: int, adults: int
    ):
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "select get_available_rooms(%s, %s, %s, %s, %s)",
                (check_in, check_out, branch, children, adults),
            )
            return cursor.fetchone().get("get_available_rooms", [])
