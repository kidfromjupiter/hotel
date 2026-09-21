import pytest
from app.api.dependencies import get_booking_repo, get_otp_service
from app.main import app
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
    with TestClient(app) as test_client:
        yield test_client
