from datetime import date
from unittest.mock import MagicMock

from app.repositories.booking_repo import BookingRepository
from app.repositories.rooms_repo import RoomsRepo
from app.schemas.booking_flow import AvailabilityRequest
from app.services.booking_service import BookingService
from app.services.booking_flow_service import BookingFlowService


def make_cursor(rows=None, row=None):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = rows or []
    cursor.fetchone.return_value = row
    return db, cursor


def test_rooms_repo_queries_available_rows():
    db, cursor = make_cursor(rows=[{"room_number": 101, "daily_rate": 25000}])
    rooms = RoomsRepo(db).get_rooms(date(2026, 10, 1), date(2026, 10, 5), "colombo", 0, 2)
    assert rooms[0]["room_number"] == 101
    sql, params = cursor.execute.call_args.args
    assert "FROM room_details" in sql and "NOT EXISTS" in sql
    assert params == ("colombo", "colombo", 2, 0, date(2026, 10, 5), date(2026, 10, 1))


def test_booking_service_shapes_availability_from_rooms_repo():
    booking_repo = MagicMock(spec=BookingRepository)
    rooms_repo = MagicMock(spec=RoomsRepo)
    rooms_repo.get_rooms.return_value = [{
        "room_number": 101, "branch_id": 1, "branch_name": "colombo",
        "room_type_id": "STANDARD", "daily_rate": 20000,
    }]
    service = BookingService(booking_repo=booking_repo, rooms_repo=rooms_repo)
    result = service.check_availability(AvailabilityRequest(
        branch="colombo", checkIn="2026-10-10", checkOut="2026-10-13", adults=2, children=0,
    ))
    assert result["rooms"][0]["totalPrice"] == 60000
    assert result["rooms"][0]["branch_name"] == "Colombo"
    rooms_repo.get_rooms.assert_called_once()


def test_booking_repo_reads_rows_and_updates_single_row():
    db, cursor = make_cursor(row={"booking_id": 500001, "booking_status": "CONFIRMED"})
    repo = BookingRepository(db)
    assert repo.find_booking_by_id(500001)["booking_id"] == 500001
    assert "FROM booking bk" in cursor.execute.call_args.args[0]

    cursor.fetchall.return_value = [{"booking_id": 500001}]
    assert repo.list_all_bookings(branch_id=1)[0]["booking_id"] == 500001
    assert "ORDER BY bk.booking_id DESC" in cursor.execute.call_args.args[0]

    cursor.fetchone.return_value = {"booking_id": 500001}
    repo.find_booking_by_id = MagicMock(return_value={"booking_status": "CHECKED_IN"})
    assert repo.update_booking(500001, {"booking_status": "CHECKED_IN"})["booking_status"] == "CHECKED_IN"
    sql, params = cursor.execute.call_args.args
    assert "UPDATE booking" in sql and "RETURNING booking_id" in sql
    assert params[-2:] == ("CONFIRMED", "CONFIRMED")


def test_booking_flow_service_is_consolidated():
    assert BookingFlowService is BookingService
