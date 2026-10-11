import os
from datetime import date, timedelta
from uuid import uuid4

import psycopg2
import pytest

from app.repositories.booking_repo import BookingRepository
from app.repositories.guests_repo import GuestsRepo


@pytest.fixture
def service_booking():
    dsn = os.environ["DATABASE_URL"]
    db = psycopg2.connect(dsn)
    assert db.info.dbname == "app_test_db", "Use the isolated test database"
    prefix = "SERVICE_TEST_" + uuid4().hex

    try:
        guest = GuestsRepo(db).create_guest("+94770000114", prefix)
        start = date(2100, 1, 1) + timedelta(
            days=int(uuid4().hex[:4], 16) * 4
        )
        booking = BookingRepository(db).save_booking({
            "room_number": 101,
            "branch_id": 1,
            "guest_id": guest["guest_id"],
            "booking_status": "CONFIRMED",
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=3)).isoformat(),
            "adult_count": 1,
            "children_count": 0,
            "grand_total": 15000,
        })

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT service_id FROM service_catalogue "
                "ORDER BY service_id DESC LIMIT 1"
            )
            service_id = cursor.fetchone()[0]
        db.commit()
        yield db, dsn, booking["booking_id"], service_id
    finally:
        db.rollback()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT booking_id FROM booking WHERE guest_id IN "
                "(SELECT guest_id FROM guests WHERE name = %s)",
                (prefix,),
            )
            ids = [row[0] for row in cursor.fetchall()]
            if ids:
                cursor.execute(
                    "DELETE FROM service_charges WHERE booking_id = ANY(%s)",
                    (ids,),
                )
                cursor.execute(
                    "DELETE FROM billing_summary WHERE booking_id = ANY(%s)",
                    (ids,),
                )
                cursor.execute(
                    "DELETE FROM booking WHERE booking_id = ANY(%s)", (ids,)
                )
            cursor.execute("DELETE FROM guests WHERE name = %s", (prefix,))
        db.commit()
        db.close()


def test_repository_commits_service_charge_and_bill(service_booking):
    db, dsn, booking_id, service_id = service_booking

    with db.cursor() as cursor:
        cursor.execute(
            "SELECT total_service_charges, grand_total "
            "FROM billing_summary WHERE booking_id = %s",
            (booking_id,),
        )
        before = cursor.fetchone()
    assert before is not None
    db.commit()

    BookingRepository(db).add_service_to_booking(
        booking_id, service_id, 2
    )

    # A separate connection proves that the repository committed the save.
    observer = psycopg2.connect(dsn)
    try:
        with observer.cursor() as cursor:
            cursor.execute(
                "SELECT service_id, service_dates, service_total "
                "FROM service_charges WHERE booking_id = %s",
                (booking_id,),
            )
            charges = cursor.fetchall()
            assert len(charges) == 1
            assert charges[0][:2] == (service_id, 2)
            charge_total = charges[0][2]
            assert charge_total is not None

            cursor.execute(
                "SELECT total_service_charges, grand_total "
                "FROM billing_summary WHERE booking_id = %s",
                (booking_id,),
            )
            after = cursor.fetchone()

        assert after[0] == (before[0] or 0) + charge_total
        assert after[1] == (before[1] or 0) + charge_total
    finally:
        observer.close()


def test_failed_save_rolls_back_and_connection_remains_usable(service_booking):
    db, _, booking_id, service_id = service_booking

    with db.cursor() as cursor:
        cursor.execute("SELECT 1 FROM booking WHERE booking_id = -1")
        assert cursor.fetchone() is None
    db.commit()

    with pytest.raises(psycopg2.Error):
        BookingRepository(db).add_service_to_booking(-1, service_id, 1)

    # This query would fail if the connection remained in an aborted transaction.
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM service_charges WHERE booking_id = %s",
            (booking_id,),
        )
        assert cursor.fetchone()[0] == 0
