from datetime import date
from uuid import uuid4

import psycopg2
import pytest

from app.repositories.billing_repo import BillingRepo
from app.repositories.booking_repo import BookingRepository
from app.repositories.branches_repo import BranchesRepo
from app.repositories.guests_repo import GuestsRepo
from app.repositories.reports_repo import ReportsRepo
from app.repositories.rooms_repo import RoomsRepo
from app.repositories.services_repo import ServicesRepo
from app.services.booking_service import BookingService
from app.services.guest_service import GuestService


def test_repository_reads_and_service_shaping_against_postgres(db_connection):
    bookings = BookingRepository(db_connection)
    guests = GuestsRepo(db_connection)
    billing = BillingRepo(db_connection)
    reports = ReportsRepo(db_connection)

    booking = bookings.find_booking_by_id(1001)
    assert booking["booking_ref"] == "SKN-1001"
    assert bookings.find_booking_by_ref("SKN-1001")["booking_id"] == 1001
    assert any(row["booking_id"] == 1001 for row in bookings.list_all_bookings(guest_id=booking["guest_id"]))
    assert any(row["booking_id"] == 1001 for row in bookings.get_admin_reservations_list(branch_id=booking["branch_id"]))
    detail = BookingService(booking_repo=bookings).get_booking_by_id(1001)
    assert detail.booking_ref == "SKN-1001"
    assert detail.service_charges

    guest = guests.get_guest_by_id(booking["guest_id"])
    assert guests.get_guest_by_phone("0" + guest["phone_number"][3:])["guest_id"] == guest["guest_id"]
    assert any(row["guest_id"] == guest["guest_id"] for row in guests.get_all_guests())
    history = GuestService(guests).get_payment_history(str(guest["guest_id"]), booking["branch_id"])
    assert history["guest"]["guest_id"] == guest["guest_id"]
    assert any(row["booking_id"] == 1001 for row in history["bookings"])

    assert any(row["booking_id"] == 1001 for row in billing.get_all_invoices())
    assert billing.get_active_stays()
    assert BranchesRepo(db_connection).get_branches()
    assert ServicesRepo(db_connection).get_services()
    assert RoomsRepo(db_connection).get_rooms(date(2100, 1, 1), date(2100, 1, 2), "colombo", 0, 1)

    assert reports.get_occupancy_data(date(2026, 9, 1), date(2026, 10, 1))
    assert reports.get_guest_billing_data()
    assert reports.get_service_usage_data()
    assert reports.get_monthly_revenue_data(2026)
    assert reports.get_service_trends_data()


def test_retained_database_boundary(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT proname FROM pg_proc
            WHERE proname = ANY(%s)
            """,
            (["create_booking", "add_service_to_booking", "extend_booking_stay",
              "record_invoice_payment", "checkout_booking", "get_booking_by_id",
              "get_all_invoices", "update_guest_phone"],),
        )
        names = {row[0] for row in cursor.fetchall()}
        cursor.execute("SELECT 1 FROM pg_constraint WHERE conname = 'booking_no_overlap' AND contype = 'x'")
        constraint = cursor.fetchone()
    assert {"create_booking", "add_service_to_booking", "extend_booking_stay",
            "record_invoice_payment", "checkout_booking"} <= names
    assert not {"get_booking_by_id", "get_all_invoices", "update_guest_phone"} & names
    assert constraint is not None


def test_single_row_updates_use_repository_sql(db_connection):
    guests = GuestsRepo(db_connection)
    booking_repo = BookingRepository(db_connection)
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT guest_id FROM guests ORDER BY guest_id LIMIT 1")
        guest_id = cursor.fetchone()[0]
        cursor.execute("SELECT membership_id FROM skynest_membership ORDER BY membership_id LIMIT 1")
        membership_id = cursor.fetchone()[0]
        cursor.execute("SELECT booking_id FROM booking WHERE booking_status = 'CONFIRMED' ORDER BY booking_id LIMIT 1")
        booking_id = cursor.fetchone()[0]

    assert guests.update_guest_phone(guest_id, "0771234560")["phone_number"] == "+94771234560"
    assert guests.enroll_guest_membership(guest_id, membership_id)["membership_id"] == membership_id
    assert booking_repo.update_booking(booking_id, {"booking_status": "CANCELLED"})["booking_status"] == "CANCELLED"
    assert booking_repo.update_booking(booking_id, {"booking_status": "CHECKED_IN"}) is None


def test_guest_and_booking_creation_roll_back_together(db_connection):
    name = "BOUNDARY_TEST_" + uuid4().hex
    guest = GuestsRepo(db_connection).create_guest("+94770000999", name)
    assert guest is not None
    assert guest["phone_number"] == "+94770000999"
    with pytest.raises(psycopg2.Error):
        BookingRepository(db_connection).save_booking({
            "guest_id": guest["guest_id"], "branch_id": 999999, "room_number": 1,
            "start_date": "2100-01-01", "end_date": "2100-01-02",
            "adult_count": 1, "children_count": 0, "grand_total": 100,
        })
    db_connection.rollback()
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM guests WHERE guest_id = %s", (guest["guest_id"],))
        assert cursor.fetchone() is None
