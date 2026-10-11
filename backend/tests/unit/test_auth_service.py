from datetime import timedelta
from unittest.mock import MagicMock

from app.repositories.staff_repo import StaffRepo
from app.services.auth_service import AuthService


def make_service(repo=None) -> AuthService:
    return AuthService(
        repo=repo,
        secret_key="test-secret",
        algorithm="HS256",
        expire_minutes=60,
    )


def test_access_token_round_trip_for_guest_claims():
    service = make_service()

    token = service.create_access_token(
        {"sub": "+94770000000", "guest_id": 42, "role": "guest"}
    )

    payload = service.decode_token(token)
    assert payload is not None
    assert payload["guest_id"] == 42
    assert payload["role"] == "guest"


def test_expired_access_token_is_rejected():
    service = make_service()
    token = service.create_access_token(
        {"sub": "1", "role": "admin"},
        expires_delta=timedelta(seconds=-1),
    )

    assert service.decode_token(token) is None


def test_staff_authentication_uses_repository_and_bcrypt_hash():
    repo = MagicMock(spec=StaffRepo)
    service = make_service(repo)
    password_hash = service.hash_password("correct-password")
    staff = {
        "staff_id": 1,
        "username": "admin",
        "password_hash": password_hash,
        "is_active": True,
    }
    repo.get_by_username.return_value = staff

    assert service.authenticate_user("admin", "correct-password") == staff
    assert service.authenticate_user("admin", "wrong-password") is None


def test_inactive_staff_cannot_authenticate():
    repo = MagicMock(spec=StaffRepo)
    repo.get_by_username.return_value = {
        "password_hash": make_service().hash_password("password"),
        "is_active": False,
    }

    assert make_service(repo).authenticate_user("disabled", "password") is None
