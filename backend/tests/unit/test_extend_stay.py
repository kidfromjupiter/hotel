from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.dependencies import get_booking_service, get_current_user
from app.main import app
from app.repositories.booking_repo import BookingRepository
from app.schemas.auth import StaffUser
from app.services.booking_service import BookingService


def successful_extension():
    return {
        "success": True,
        "message": "Stay extended successfully.",
        "booking_id": 1001,
        "previous_check_out_date": "2026-09-05",
        "new_check_out_date": "2026-09-07",
        "added_nights": 2,
        "added_room_charge": 30000.0,
        "grand_total": 108200.0,
        "payment_status": "PARTIALLY_PAID",
    }


def test_repository_calls_extend_stay_database_function():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"extend_booking_stay": successful_extension()}

    result = BookingRepository(mock_db).extend_stay(1001, date(2026, 9, 7))

    assert result["success"] is True
    assert result["added_nights"] == 2
    mock_cursor.execute.assert_called_once_with(
        "SELECT extend_booking_stay(%s, %s)",
        (1001, date(2026, 9, 7)),
    )


def test_service_returns_typed_extension_response():
    repo = MagicMock(spec=BookingRepository)
    repo.extend_stay.return_value = successful_extension()

    response = BookingService(booking_repo=repo).extend_stay(
        1001, date(2026, 9, 7)
    )

    assert response.booking_id == 1001
    assert response.new_check_out_date == date(2026, 9, 7)
    assert response.payment_status == "PARTIALLY_PAID"


@pytest.mark.parametrize(
    ("error_code", "expected_status"),
    [
        ("NOT_FOUND", 404),
        ("OVERLAP", 409),
        ("INVALID_STATUS", 400),
        ("INVALID_DATE", 400),
        ("BILLING_NOT_FOUND", 400),
    ],
)
def test_service_maps_extension_errors(error_code, expected_status):
    repo = MagicMock(spec=BookingRepository)
    repo.extend_stay.return_value = {
        "success": False,
        "error_code": error_code,
        "message": "Extension rejected.",
    }

    with pytest.raises(HTTPException) as exc_info:
        BookingService(booking_repo=repo).extend_stay(
            1001, date(2026, 9, 7)
        )

    assert exc_info.value.status_code == expected_status
    assert exc_info.value.detail == "Extension rejected."


def test_get_booking_record_rejects_missing_booking():
    repo = MagicMock(spec=BookingRepository)
    repo.find_booking_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        BookingService(booking_repo=repo).get_booking_record(999999)

    assert exc_info.value.status_code == 404


def test_extend_stay_api_success(client):
    service = MagicMock(spec=BookingService)
    service.get_booking_record.return_value = {"booking_id": 1001, "branch_id": 1}
    service.extend_stay.return_value = successful_extension()
    app.dependency_overrides[get_booking_service] = lambda: service

    try:
        response = client.post(
            "/api/v1/private/bookings/1001/extend",
            json={"new_check_out_date": "2026-09-07"},
        )
    finally:
        app.dependency_overrides.pop(get_booking_service, None)

    assert response.status_code == 200
    assert response.json()["added_nights"] == 2
    service.extend_stay.assert_called_once_with(1001, date(2026, 9, 7))


def test_extend_stay_api_enforces_receptionist_branch(client):
    service = MagicMock(spec=BookingService)
    service.get_booking_record.return_value = {"booking_id": 1001, "branch_id": 1}
    app.dependency_overrides[get_booking_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: StaffUser(
        staff_id=2,
        branch_id=2,
        username="kandy_reception",
        full_name="Kandy Receptionist",
        role="receptionist",
        is_active=True,
    )

    try:
        response = client.post(
            "/api/v1/private/bookings/1001/extend",
            json={"new_check_out_date": "2026-09-07"},
        )
    finally:
        app.dependency_overrides.pop(get_booking_service, None)
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    service.extend_stay.assert_not_called()
