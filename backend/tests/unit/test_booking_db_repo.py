from datetime import date
from unittest.mock import MagicMock

from app.repositories.booking_repo import BookingRepository
from app.repositories.rooms_repo import RoomsRepo
from app.schemas.booking_flow import AvailabilityRequest
from app.services.booking_service import BookingService
from app.services.booking_flow_service import BookingFlowService


def test_rooms_repo_calls_db_function():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {
        "get_available_rooms": [
            {
                "room_number": 101,
                "branch_id": 1,
                "room_type_id": "STANDARD",
                "room_status": "AVAILABLE",
                "capacity": 2,
                "price_per_night": 25000,
            }
        ]
    }

    repo = RoomsRepo(db=mock_db)
    rooms = repo.get_rooms(date(2026, 10, 1), date(2026, 10, 5), "colombo", 0, 2)

    assert len(rooms) == 1
    assert rooms[0]["room_number"] == 101
    mock_cursor.execute.assert_called_once()
    assert "get_available_rooms" in mock_cursor.execute.call_args[0][0]


def test_booking_repo_get_available_rooms_calls_db_function():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {
        "get_available_rooms": [
            {
                "room_number": 201,
                "branch_id": 1,
                "room_type_id": "DELUXE",
                "capacity": 3,
                "price_per_night": 35000,
            }
        ]
    }

    repo = BookingRepository(db=mock_db)
    rooms = repo.get_available_rooms(
        check_in=date(2026, 10, 10),
        check_out=date(2026, 10, 13),
        branch="colombo",
        children=1,
        adults=2,
    )

    assert len(rooms) == 1
    assert rooms[0]["room_number"] == 201
    mock_cursor.execute.assert_called_once()
    sql_query = mock_cursor.execute.call_args[0][0]
    assert "get_available_rooms" in sql_query


def test_booking_service_check_availability_uses_db_function():
    mock_repo = MagicMock(spec=BookingRepository)
    mock_repo.get_available_rooms.return_value = [
        {
            "room_number": 101,
            "branch_id": 1,
            "room_type_id": "STANDARD",
            "capacity": 2,
            "price_per_night": 20000,
        }
    ]

    service = BookingService(booking_repo=mock_repo)
    req = AvailabilityRequest(
        branch="colombo",
        checkIn="2026-10-10",
        checkOut="2026-10-13",
        adults=2,
        children=0,
    )
    result = service.check_availability(req)

    assert result["available"] is True
    assert len(result["rooms"]) == 1
    assert result["rooms"][0]["nights"] == 3
    assert result["rooms"][0]["totalPrice"] == 60000
    mock_repo.get_available_rooms.assert_called_once()


def test_booking_repo_db_crud_functions():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor

    # 1. find_booking_by_id calls get_booking_by_id
    mock_cursor.fetchone.return_value = {
        "get_booking_by_id": {
            "booking_id": 500001,
            "guest_name": "Test User",
            "booking_status": "Confirmed",
        }
    }
    repo = BookingRepository(db=mock_db)
    booking = repo.find_booking_by_id(500001)
    assert booking["booking_id"] == 500001
    assert "get_booking_by_id" in mock_cursor.execute.call_args[0][0]

    # 2. list_all_bookings calls get_all_bookings
    mock_cursor.fetchone.return_value = {
        "get_all_bookings": [
            {"booking_id": 500001, "booking_status": "Confirmed"}
        ]
    }
    bookings = repo.list_all_bookings(branch_id=1)
    assert len(bookings) == 1
    assert "get_all_bookings" in mock_cursor.execute.call_args[0][0]

    # 3. update_booking calls update_booking_status
    mock_cursor.fetchone.return_value = {
        "update_booking_status": {
            "booking_id": 500001,
            "booking_status": "Checked-In",
        }
    }
    updated = repo.update_booking(500001, {"booking_status": "Checked-In"})
    assert updated["booking_status"] == "Checked-In"
    assert "update_booking_status" in mock_cursor.execute.call_args[0][0]


def test_booking_flow_service_is_consolidated():
    assert BookingFlowService is BookingService
