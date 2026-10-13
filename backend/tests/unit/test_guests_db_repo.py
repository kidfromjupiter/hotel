from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.repositories.guests_repo import GuestsRepo
from app.schemas.auth import StaffUser
from app.services.guest_service import GuestService


def test_guests_repo_calls_db_functions():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor

    # 1. get_all_guests
    mock_cursor.fetchone.return_value = {
        "get_all_guests": [
            {
                "guest_id": 101,
                "name": "Sunil Silva",
                "national_id": "199012345678",
                "phone_number": "771112233",
                "membership_id": 1,
                "membership_name": "Gold",
                "room_discount_percentage": 10.0,
                "service_discount_percentage": 5.0,
            }
        ]
    }
    repo = GuestsRepo(db=mock_db)
    guests = repo.get_all_guests(search="Sunil")
    assert len(guests) == 1
    assert guests[0]["name"] == "Sunil Silva"
    assert "get_all_guests" in mock_cursor.execute.call_args[0][0]

    # 2. get_guest_by_phone
    mock_cursor.fetchone.return_value = {
        "get_guest_by_phone": {
            "guest_id": 101,
            "name": "Sunil Silva",
            "phone_number": "771112233",
            "has_membership": True,
            "room_discount_percentage": 10.0,
        }
    }
    guest = repo.get_guest_by_phone("+94771112233")
    assert guest is not None
    assert guest["has_membership"] is True
    assert "get_guest_by_phone" in mock_cursor.execute.call_args[0][0]

    # 3. get_guest_by_id
    mock_cursor.fetchone.return_value = {
        "get_guest_by_id": {
            "guest_id": 101,
            "name": "Sunil Silva",
            "has_membership": True,
        }
    }
    g_id = repo.get_guest_by_id(101)
    assert g_id["guest_id"] == 101
    assert "get_guest_by_id" in mock_cursor.execute.call_args[0][0]

    # 4. get_payment_history
    payment_history = {
        "guest": {"guest_id": 101, "name": "Sunil Silva", "phone_number": "771112233"},
        "summary": {
            "booking_count": 1,
            "grand_total": 1000.0,
            "amount_paid": 400.0,
            "outstanding_balance": 600.0,
        },
        "bookings": [],
    }
    mock_cursor.fetchone.return_value = {
        "get_guest_payment_history": payment_history
    }
    history = repo.get_payment_history(" 101 ", branch_id=2)
    assert history == payment_history
    assert "get_guest_payment_history" in mock_cursor.execute.call_args[0][0]
    assert mock_cursor.execute.call_args[0][1] == ("101", 2)

    # 5. update_guest_phone
    mock_cursor.fetchone.return_value = {
        "update_guest_phone": {
            "success": True,
            "message": "Phone number updated successfully",
            "guest_id": 101,
            "phone_number": "778889900",
        }
    }
    res_up = repo.update_guest_phone(101, "0778889900")
    assert res_up["success"] is True
    assert "update_guest_phone" in mock_cursor.execute.call_args[0][0]

    # 6. enroll_guest_membership
    mock_cursor.fetchone.return_value = {
        "enroll_guest_membership": {
            "success": True,
            "message": "Guest enrolled in membership successfully",
            "guest_id": 101,
            "membership_id": 2,
        }
    }
    res_enroll = repo.enroll_guest_membership(101, 2)
    assert res_enroll["success"] is True
    assert "enroll_guest_membership" in mock_cursor.execute.call_args[0][0]


def test_guests_repo_without_db():
    repo = GuestsRepo(db=None)
    assert repo.get_all_guests() == []
    assert repo.get_guest_by_id(1) is None
    assert repo.get_guest_by_phone("0771234567") is None
    assert repo.get_payment_history("1", branch_id=1) is None


def test_guest_service_delegates_to_repo():
    mock_repo = MagicMock(spec=GuestsRepo)
    mock_repo.get_all_guests.return_value = [{"guest_id": 1, "name": "Alice"}]
    mock_repo.get_guest_by_id.return_value = {"guest_id": 1, "name": "Alice"}
    mock_repo.get_guest_by_phone.return_value = {"guest_id": 1, "has_membership": True}
    mock_repo.get_payment_history.return_value = {
        "guest": {"guest_id": 1},
        "summary": {"booking_count": 0},
        "bookings": [],
    }

    svc = GuestService(repo=mock_repo)
    assert len(svc.list_guests()) == 1
    assert svc.get_guest(1)["name"] == "Alice"
    assert svc.lookup_by_phone("0771234567")["has_membership"] is True
    assert svc.get_payment_history("1", branch_id=3)["guest"]["guest_id"] == 1
    mock_repo.get_payment_history.assert_called_once_with(query="1", branch_id=3)


def test_guest_payment_status_api_is_branch_scoped(monkeypatch):
    captured = {}
    payment_history = {
        "guest": {
            "guest_id": 1,
            "name": "Nimal Fernando",
            "phone_number": "771234567",
        },
        "summary": {
            "booking_count": 2,
            "grand_total": 1500.0,
            "amount_paid": 1000.0,
            "outstanding_balance": 500.0,
        },
        "bookings": [
            {
                "booking_id": 1001,
                "booking_ref": "SKN-1001",
                "branch_id": 2,
                "branch_name": "Kandy",
                "start_date": "2026-10-01",
                "end_date": "2026-10-02",
                "booking_status": "CHECKED_OUT",
                "invoice_id": "11111111-1111-1111-1111-111111111111",
                "payment_method": "CARD",
                "payment_status": "PARTIALLY_PAID",
                "grand_total": 1500.0,
                "amount_paid": 1000.0,
                "outstanding_balance": 500.0,
            }
        ],
    }

    def fake_history(self, query, branch_id=None):
        captured.update(query=query, branch_id=branch_id)
        return payment_history

    monkeypatch.setattr(GuestsRepo, "get_payment_history", fake_history)
    app.dependency_overrides[get_current_user] = lambda: StaffUser(
        staff_id=5,
        branch_id=2,
        username="reception",
        full_name="Reception User",
        role="receptionist",
        is_active=True,
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/private/guests/payment-status?query=%2B94%2077%20123%204567"
            )
        assert response.status_code == 200
        assert response.json()["summary"]["outstanding_balance"] == 500.0
        assert captured == {"query": "+94 77 123 4567", "branch_id": 2}
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_guest_payment_status_api_returns_404(monkeypatch):
    monkeypatch.setattr(
        GuestsRepo,
        "get_payment_history",
        lambda self, query, branch_id=None: None,
    )
    app.dependency_overrides[get_current_user] = lambda: StaffUser(
        staff_id=1,
        branch_id=None,
        username="admin",
        full_name="Administrator",
        role="admin",
        is_active=True,
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/private/guests/payment-status?query=missing"
            )
        assert response.status_code == 404
        assert response.json()["detail"] == "Guest not found"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_guests_api_endpoints(monkeypatch):
    test_guests = [
        {
            "guest_id": 1,
            "name": "Nimal Fernando",
            "national_id": "198512345678",
            "phone_number": "771234567",
            "membership_id": 1,
            "membership_name": "Gold",
            "room_discount_percentage": 10.0,
            "service_discount_percentage": 5.0,
            "has_membership": True,
        },
        {
            "guest_id": 2,
            "name": "Sarah Connor",
            "national_id": "199098765432",
            "phone_number": "719988776",
            "membership_id": None,
            "membership_name": "None",
            "room_discount_percentage": 0.0,
            "service_discount_percentage": 0.0,
            "has_membership": False,
        },
    ]
    monkeypatch.setattr(GuestsRepo, "get_all_guests", lambda self, search=None: test_guests)
    monkeypatch.setattr(GuestsRepo, "get_guest_by_id", lambda self, gid: next((g for g in test_guests if g["guest_id"] == gid), None))
    monkeypatch.setattr(GuestsRepo, "get_guest_by_phone", lambda self, phone: test_guests[0])
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: StaffUser(
            staff_id=1,
            branch_id=None,
            username="admin",
            full_name="Administrator",
            role="admin",
            is_active=True,
        ),
    )

    client = TestClient(app)

    # 1. GET /api/v1/private/guests/
    res = client.get("/api/v1/private/guests/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # 2. GET /api/v1/private/guests/1
    res_single = client.get("/api/v1/private/guests/1")
    assert res_single.status_code == 200
    assert res_single.json()["guest_id"] == 1

    # 3. GET /api/v1/private/guests/lookup/phone
    res_lookup = client.get("/api/v1/private/guests/lookup/phone?phone=0771234567")
    assert res_lookup.status_code == 200
    assert res_lookup.json()["name"] == "Nimal Fernando"

    # 4. POST /api/v1/public/otp/send verifies membership lookup
    res_otp = client.post("/api/v1/public/otp/send", json={"phone": "0771234567"})
    assert res_otp.status_code == 200
    otp_json = res_otp.json()
    assert otp_json["success"] is True
    assert otp_json["hasMembership"] is True
