from fastapi import APIRouter, Depends
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
from app.db import get_db

router = APIRouter()

@router.get("/")
def list_guests(db: connection = Depends(get_db)):
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT guest_id, name, national_id, phone_number, membership_id FROM guests")
        return cursor.fetchall()
