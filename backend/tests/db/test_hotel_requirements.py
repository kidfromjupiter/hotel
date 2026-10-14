from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import os
from threading import Barrier

import psycopg2

from app.repositories.reports_repo import ReportsRepo


def test_seed_counts_and_derived_availability(db_connection):
    with db_connection.cursor() as cursor:
        for table, expected in [
            ("branches", 3), ("room_details", 15), ("service_catalogue", 7),
            ("guests", 5),
        ]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            assert cursor.fetchone()[0] == expected
        cursor.execute("SELECT COUNT(*) FROM booking WHERE booking_id BETWEEN 1001 AND 1008")
        assert cursor.fetchone()[0] == 8
        cursor.execute("SELECT COUNT(*) FROM billing_summary WHERE payment_status = 'PARTIALLY_PAID'")
        assert cursor.fetchone()[0] >= 3
        cursor.execute("SELECT room_number, available FROM room_availability(CURRENT_DATE, CURRENT_DATE + 1) WHERE branch_id = 1 AND room_number IN (101, 102) ORDER BY room_number")
        assert cursor.fetchall() == [(101, True), (102, False)]


def test_service_snapshot_and_bill_recalculation(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT grand_total FROM billing_summary WHERE booking_id = 1001")
        old_total = cursor.fetchone()[0]
        cursor.execute("SELECT add_service_to_booking(1001, 2, 2, CURRENT_DATE)")
        result = cursor.fetchone()[0]
        assert result["success"] is True
        cursor.execute("UPDATE service_catalogue SET day_rate = 9999 WHERE service_id = 2")
        cursor.execute("SELECT quantity, unit_price, service_total FROM service_charges WHERE service_log_id = %s", (result["service_log_id"],))
        assert cursor.fetchone() == (2, Decimal("1500.00"), Decimal("2850.00"))
        cursor.execute("SELECT grand_total, payment_status FROM billing_summary WHERE booking_id = 1001")
        total, status = cursor.fetchone()
        assert total == old_total + Decimal("3277.50")
        assert status == "PARTIALLY_PAID"


def test_monthly_revenue_uses_payment_allocations(db_connection):
    rows = ReportsRepo(db_connection).get_monthly_revenue_data(date.today().year, 1)
    assert rows
    for row in rows:
        assert row["total_revenue"] == row["room_revenue"] + row["service_revenue"] + row["tax_revenue"]


def test_concurrent_overlapping_bookings_allow_only_one():
    dsn = os.environ["DATABASE_URL"]
    barrier = Barrier(2)
    start = date(2201, 1, 1)

    def insert():
        db = psycopg2.connect(dsn)
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT nextval(pg_get_serial_sequence('booking', 'booking_id'))")
                booking_id = cursor.fetchone()[0]
                barrier.wait(timeout=10)
                cursor.execute(
                    """INSERT INTO booking (booking_id, booking_ref, room_number, branch_id,
                       guest_id, booking_status, start_date, end_date, adult_count, children_count)
                       VALUES (%s, %s, 202, 1, 1, 'CONFIRMED', %s, %s, 1, 0)""",
                    (booking_id, f"SKN-{booking_id}", start, start + timedelta(days=2)),
                )
            db.commit()
            return booking_id
        except (psycopg2.errors.ExclusionViolation, psycopg2.errors.DeadlockDetected):
            db.rollback()
            return None
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        winners = list(pool.map(lambda _: insert(), range(2)))
    assert sum(value is not None for value in winners) == 1
    with psycopg2.connect(dsn) as cleanup:
        with cleanup.cursor() as cursor:
            cursor.execute("DELETE FROM booking WHERE booking_id = %s", (next(value for value in winners if value),))
