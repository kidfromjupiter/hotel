import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Barrier
from uuid import uuid4

import psycopg2
import pytest

from app.repositories.booking_repo import BookingRepository
from app.repositories.guests_repo import GuestsRepo


@pytest.fixture
def test_database():
    dsn = os.environ["DATABASE_URL"]
    connection = psycopg2.connect(dsn)
    assert connection.info.dbname == "app_test_db", "Use the isolated test database"
    prefix = "PK_TEST_" + uuid4().hex

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM room_details "
            "WHERE room_number = 101 AND branch_id = 1)"
        )
        assert cursor.fetchone()[0], "Load seed.sql before running these tests"
        cursor.execute("SELECT EXISTS (SELECT 1 FROM service_catalogue WHERE service_id = 1)")
        assert cursor.fetchone()[0], "Seed service 1 is required"
    connection.commit()

    try:
        yield dsn, prefix
    finally:
        connection.rollback()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT booking_id FROM booking WHERE guest_id IN "
                "(SELECT guest_id FROM guests WHERE name LIKE %s)",
                (prefix + "%",),
            )
            ids = [row[0] for row in cursor.fetchall()]
            if ids:
                cursor.execute("DELETE FROM service_charges WHERE booking_id = ANY(%s)", (ids,))
                cursor.execute("DELETE FROM billing_summary WHERE booking_id = ANY(%s)", (ids,))
                cursor.execute("DELETE FROM booking WHERE booking_id = ANY(%s)", (ids,))
            cursor.execute("DELETE FROM guests WHERE name LIKE %s", (prefix + "%",))
        connection.commit()
        connection.close()


@pytest.mark.parametrize("kind", ["guest", "booking", "service"])
def test_concurrent_ids_are_unique_and_persisted(test_database, kind):
    dsn, prefix = test_database
    table, column = {
        "guest": ("guests", "guest_id"),
        "booking": ("booking", "booking_id"),
        "service": ("service_charges", "service_log_id"),
    }[kind]

    setup = psycopg2.connect(dsn)
    try:
        guest = GuestsRepo(setup).create_guest("+94770000111", prefix + "_owner")
        assert guest is not None
        guest_id = guest["guest_id"]
        start = date(2100, 1, 1) + timedelta(days=int(uuid4().hex[:4], 16) * 4)

        def booking_payload(index):
            check_in = start + timedelta(days=index * 2)
            return {
                "room_number": 101,
                "branch_id": 1,
                "branch": "colombo",
                "guest_id": guest_id,
                "booking_status": "CONFIRMED",
                "start_date": check_in.isoformat(),
                "end_date": (check_in + timedelta(days=1)).isoformat(),
                "adult_count": 1,
                "children_count": 0,
                "grand_total": 15000,
            }

        service_booking = None
        if kind == "service":
            service_booking = BookingRepository(setup).save_booking(booking_payload(0))["booking_id"]

        with setup.cursor() as cursor:
            cursor.execute(f"SELECT COALESCE(MAX({column}), 0) FROM {table}")
            previous_max = cursor.fetchone()[0]
        setup.commit()

        barrier = Barrier(2)

        def insert(index):
            db = psycopg2.connect(dsn)
            try:
                barrier.wait(timeout=10)
                if kind == "guest":
                    result = GuestsRepo(db).create_guest(
                        "+94770000112", prefix + "_" + str(index)
                    )
                    assert result is not None
                    return result["guest_id"]
                if kind == "booking":
                    return BookingRepository(db).save_booking(
                        booking_payload(index)
                    )["booking_id"]
                with db.cursor() as cursor:
                    cursor.execute(
                        "SELECT add_service_to_booking(%s, %s, %s)",
                        (service_booking, 1, 1),
                    )
                    result = cursor.fetchone()[0]
                assert result["success"] is True
                db.commit()
                return result["service_log_id"]
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            ids = list(executor.map(insert, range(2)))

        assert len(set(ids)) == 2, "Concurrent requests received duplicate IDs"
        assert min(ids) > previous_max, "Generated ID collided with existing data"

        with setup.cursor() as cursor:
            cursor.execute(
                f"SELECT {column} FROM {table} WHERE {column} = ANY(%s)",
                (ids,),
            )
            persisted = {row[0] for row in cursor.fetchall()}
        assert persisted == set(ids), "Returned IDs were not saved in PostgreSQL"
    finally:
        setup.close()
