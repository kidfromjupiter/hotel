from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.repositories.booking_repo import BookingRepository
from app.services.booking_service import BookingService


def test_repository_saves_requested_service():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value

    BookingRepository(db=db).add_service_to_booking(1001, 2, 3)

    cursor.execute.assert_called_once_with(
        "SELECT add_service_to_booking(%s, %s, %s)",
        (1001, 2, 3),
    )
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


@pytest.mark.parametrize("failure_stage", ["execute", "commit"])
def test_repository_rolls_back_and_propagates_failure(failure_stage):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    error = RuntimeError("Database operation failed")

    if failure_stage == "execute":
        cursor.execute.side_effect = error
    else:
        db.commit.side_effect = error

    with pytest.raises(RuntimeError) as caught:
        BookingRepository(db=db).add_service_to_booking(1001, 2, 3)

    assert caught.value is error
    db.rollback.assert_called_once()
    if failure_stage == "execute":
        db.commit.assert_not_called()


def test_repository_rejects_missing_database():
    with pytest.raises(RuntimeError, match="Database connection is unavailable"):
        BookingRepository(db=None).add_service_to_booking(1001, 2, 3)


@pytest.mark.parametrize("status", ["CONFIRMED", "CHECKED_IN"])
def test_service_delegates_and_returns_updated_booking(status):
    repo = MagicMock(spec=BookingRepository)
    repo.find_booking_by_id.return_value = {"booking_status": status}
    service = BookingService(booking_repo=repo)
    payload = SimpleNamespace(service_id=2, service_dates=3)
    updated = object()

    with patch.object(service, "get_booking_by_id", return_value=updated) as read:
        result = service.add_service_to_booking(1001, payload)

    repo.add_service_to_booking.assert_called_once_with(1001, 2, 3)
    read.assert_called_once_with(1001)
    assert result is updated


@pytest.mark.parametrize(
    "booking, expected_status",
    [
        (None, 404),
        ({"booking_status": "CANCELLED"}, 400),
        ({"booking_status": "CHECKED_OUT"}, 400),
    ],
)
def test_service_rejects_missing_or_inactive_booking(booking, expected_status):
    repo = MagicMock(spec=BookingRepository)
    repo.find_booking_by_id.return_value = booking
    service = BookingService(booking_repo=repo)

    with pytest.raises(HTTPException) as caught:
        service.add_service_to_booking(
            1001, SimpleNamespace(service_id=2, service_dates=3)
        )

    assert caught.value.status_code == expected_status
    repo.add_service_to_booking.assert_not_called()


def test_service_does_not_return_success_after_repository_failure():
    repo = MagicMock(spec=BookingRepository)
    repo.find_booking_by_id.return_value = {"booking_status": "CHECKED_IN"}
    error = RuntimeError("Database operation failed")
    repo.add_service_to_booking.side_effect = error
    service = BookingService(booking_repo=repo)

    with patch.object(service, "get_booking_by_id") as read:
        with pytest.raises(RuntimeError) as caught:
            service.add_service_to_booking(
                1001, SimpleNamespace(service_id=2, service_dates=3)
            )

    assert caught.value is error
    read.assert_not_called()
