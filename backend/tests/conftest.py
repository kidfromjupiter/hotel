import pytest
from app.api.dependencies import get_booking_repo, get_otp_service
from app.main import app
from fastapi.testclient import TestClient


from app.db import get_db

@pytest.fixture
def db_connection():
    generator = get_db()
    conn = next(generator)
    yield conn
    try:
        next(generator)
    except StopIteration:
        pass

@pytest.fixture
def booking_repo(db_connection):
    repo = get_booking_repo(db=db_connection)
    repo.clear()
    
    if repo.db:
        with repo.db.cursor() as cursor:
            cursor.execute("DELETE FROM billing_summary WHERE booking_id >= 90000;")
            cursor.execute("DELETE FROM booking WHERE booking_id >= 90000;")
        repo.db.commit()

    yield repo

    if repo.db:
        with repo.db.cursor() as cursor:
            cursor.execute("DELETE FROM billing_summary WHERE booking_id >= 90000;")
            cursor.execute("DELETE FROM booking WHERE booking_id >= 90000;")
        repo.db.commit()

    repo.clear()


@pytest.fixture
def otp_service():
    service = get_otp_service()
    service.clear()
    yield service
    service.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
