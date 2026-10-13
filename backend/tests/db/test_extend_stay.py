from datetime import date

from app.repositories.booking_repo import BookingRepository


def test_extend_stay_updates_dates_billing_and_payment_status(db_connection):
    result = BookingRepository(db_connection).extend_stay(
        1001, date(2026, 9, 7)
    )

    assert result["success"] is True
    assert result["previous_check_out_date"] == "2026-09-05"
    assert result["new_check_out_date"] == "2026-09-07"
    assert result["added_nights"] == 2
    assert float(result["added_room_charge"]) == 30000.0
    assert float(result["grand_total"]) == 108200.0
    assert result["payment_status"] == "PARTIALLY_PAID"

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT end_date FROM booking WHERE booking_id = 1001")
        assert cursor.fetchone()[0] == date(2026, 9, 7)
        cursor.execute(
            "SELECT total_room_charges, grand_total, payment_status "
            "FROM billing_summary WHERE booking_id = 1001"
        )
        room_charges, grand_total, payment_status = cursor.fetchone()

    assert float(room_charges) == 90000.0
    assert float(grand_total) == 108200.0
    assert payment_status == "PARTIALLY_PAID"


def test_extend_stay_rejects_overlapping_active_booking(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO booking (
                booking_id, booking_ref, room_number, branch_id, guest_id,
                booking_status, start_date, end_date, adult_count, children_count
            ) VALUES (
                990019, 'SKN-990019', 102, 1, 2,
                'CONFIRMED', '2026-09-06', '2026-09-08', 1, 0
            )
            """
        )
        cursor.execute("SELECT end_date FROM booking WHERE booking_id = 1001")
        old_end_date = cursor.fetchone()[0]
        cursor.execute(
            "SELECT total_room_charges, grand_total "
            "FROM billing_summary WHERE booking_id = 1001"
        )
        old_bill = cursor.fetchone()

    result = BookingRepository(db_connection).extend_stay(
        1001, date(2026, 9, 7)
    )

    assert result["success"] is False
    assert result["error_code"] == "OVERLAP"

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT end_date FROM booking WHERE booking_id = 1001")
        assert cursor.fetchone()[0] == old_end_date
        cursor.execute(
            "SELECT total_room_charges, grand_total "
            "FROM billing_summary WHERE booking_id = 1001"
        )
        assert cursor.fetchone() == old_bill


def test_extend_stay_rejects_booking_that_is_not_checked_in(db_connection):
    result = BookingRepository(db_connection).extend_stay(
        1002, date(2026, 9, 14)
    )

    assert result["success"] is False
    assert result["error_code"] == "INVALID_STATUS"
