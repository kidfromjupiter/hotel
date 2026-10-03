from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class GuestsRepo:
    def __init__(self, db: connection) -> None:
        self.db = db

    def get_all_guests(self):
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT guest_id, name, national_id, phone_number, membership_id FROM guests"
            )
            return cursor.fetchall()
