import os
from datetime import date, timedelta

import psycopg2
import pytest

from app.repositories.booking_repo import BookingRepository


@pytest.fixture
def db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])

    # Cleanup is allowed only in our dedicated integration database.
    if conn.get_dsn_parameters()["dbname"] != "hotel_integration":
        conn.close()
        pytest.fail("These tests require the hotel_integration database.")

    repo = BookingRepository(db=conn)

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                TRUNCATE branches, room_types, guests CASCADE;

                INSERT INTO branches (branch_id, branch_name)
                VALUES (1, 'colombo');

                INSERT INTO room_types (room_type_id, daily_rate)
                VALUES ('TEST_STANDARD', 20000);

                INSERT INTO guests (guest_id, name, phone_number)
                VALUES (1, 'Integration Guest', 770000001);

                INSERT INTO room_details
                    (room_number, branch_id, room_type_id,
                     room_status, capacity)
                VALUES
                    (101, 1, 'TEST_STANDARD', 'AVAILABLE', 2),
                    (102, 1, 'TEST_STANDARD', 'AVAILABLE', 2);
            """)
        conn.commit()
        repo.clear()
        yield conn
    finally:
        conn.rollback()
        with conn.cursor() as cursor:
            cursor.execute(
                "TRUNCATE branches, room_types, guests CASCADE"
            )
        conn.commit()
        repo.clear()
        conn.close()


def booking_payload():
    check_in = date.today() + timedelta(days=30)
    return {
        "branch": "colombo",
        "checkIn": check_in.isoformat(),
        "checkOut": (check_in + timedelta(days=2)).isoformat(),
        "adults": 1,
        "children": 0,
        "nights": 2,
        "roomId": "102",
        "roomType": "TEST_STANDARD",
        "phone": "+94770000001",
        "guest_id": 1,
        "totalPrice": 40000,
    }


def test_selected_room_is_saved_in_postgres(db):
    repo = BookingRepository(db=db)
    saved = repo.save_booking(booking_payload())

    with db.cursor() as cursor:
        cursor.execute("""
            SELECT b.room_number, b.branch_id,
                   b.start_date, b.end_date, s.grand_total
            FROM booking b
            JOIN billing_summary s USING (booking_id)
            WHERE b.booking_id = %s
        """, (saved["booking_id"],))
        row = cursor.fetchone()

    assert row is not None, "Success was returned without a database booking"
    assert row[0] == 102, "Selected room 102 was not saved"
    assert row[1] == 1
    assert (row[3] - row[2]).days == 2
    assert float(row[4]) == 40000


def test_overlapping_confirmed_bookings_are_rejected(db):
    payload = booking_payload()

    sql = """
        INSERT INTO booking
            (booking_id, room_number, branch_id, guest_id,
             booking_status, start_date, end_date,
             adult_count, children_count)
        VALUES (%s, 102, 1, 1, 'Confirmed', %s, %s, 1, 0)
    """

    with db.cursor() as cursor:
        cursor.execute(sql, (1, payload["checkIn"], payload["checkOut"]))
    db.commit()

    with pytest.raises(psycopg2.Error, match="already booked"):
        with db.cursor() as cursor:
            cursor.execute(
                sql, (2, payload["checkIn"], payload["checkOut"])
            )


def test_database_save_failure_is_not_reported_as_success(db):
    payload = booking_payload()
    payload["room_number"] = 999  # No such room: foreign-key violation.

    repo = BookingRepository(db=db)

    with pytest.raises(psycopg2.Error):
        repo.save_booking(payload)

        
@pytest.mark.parametrize("room_id", [None, "", "invalid"])
def test_invalid_room_id_does_not_create_booking(db, room_id):
    payload = booking_payload()
    payload["roomId"] = room_id
    repo = BookingRepository(db=db)

    with pytest.raises(ValueError, match="valid roomId"):
        repo.save_booking(payload)

    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM booking")
        assert cursor.fetchone()[0] == 0