from fastapi import APIRouter, Depends
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
from app.db import get_db

router = APIRouter()

@router.get("/")
def list_services(db: connection = Depends(get_db)):
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT service_id as id, service_name as name, day_rate as price FROM service_catalogue")
        return cursor.fetchall()
