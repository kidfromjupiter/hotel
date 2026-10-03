from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.guests_repo import GuestsRepo
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

    # 4. update_guest_phone
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

    # 5. enroll_guest_membership
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


def test_guests_repo_fallback_mode():
    repo = GuestsRepo(db=None)

    # List all fallback
    all_g = repo.get_all_guests()
    assert len(all_g) >= 2

    # Search filter
    sarah = repo.get_all_guests(search="sarah")
    assert len(sarah) == 1
    assert sarah[0]["name"] == "Sarah Connor"

    # Lookup phone
    member_by_phone = repo.get_guest_by_phone("0771234567")
    assert member_by_phone is not None
    assert member_by_phone["has_membership"] is True


def test_guest_service_delegates_to_repo():
    mock_repo = MagicMock(spec=GuestsRepo)
    mock_repo.get_all_guests.return_value = [{"guest_id": 1, "name": "Alice"}]
    mock_repo.get_guest_by_id.return_value = {"guest_id": 1, "name": "Alice"}
    mock_repo.get_guest_by_phone.return_value = {"guest_id": 1, "has_membership": True}

    svc = GuestService(repo=mock_repo)
    assert len(svc.list_guests()) == 1
    assert svc.get_guest(1)["name"] == "Alice"
    assert svc.lookup_by_phone("0771234567")["has_membership"] is True


def test_guests_api_endpoints():
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
