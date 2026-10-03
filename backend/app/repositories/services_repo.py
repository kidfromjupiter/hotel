from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

class ServicesRepo:
    def __init__(self, db: connection) -> None:
        self.db = db

    def get_all_services(self):
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT service_id as id, service_name as name, day_rate as price FROM service_catalogue"
            )
            return cursor.fetchall()
