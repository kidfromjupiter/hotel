import pytest
from app.api.dependencies import get_booking_repo, get_otp_service, get_current_user
from app.main import app
from app.schemas.auth import StaffUser
from fastapi.testclient import TestClient


@pytest.fixture
def booking_repo():
    repo = get_booking_repo()
    repo.clear()
    yield repo
    repo.clear()


@pytest.fixture
def otp_service():
    service = get_otp_service()
    service.clear()
    yield service
    service.clear()


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: StaffUser(
        staff_id=1,
        branch_id=None,
        username="admin",
        full_name="System Administrator",
        role="admin",
        is_active=True,
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_user, None)
