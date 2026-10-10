from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.billing_repo import BillingRepo
from app.repositories.services_repo import ServicesRepo
from app.services.billing_service import BillingService
from app.services.services_service import ServicesService


def test_services_repo_calls_db():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor

    # 1. get_services
    mock_cursor.fetchone.return_value = {
        "get_all_services": [
            {
                "service_id": 1,
                "service_name": "Spa",
                "day_rate": 10000.0,
                "description": "Relaxing spa",
            }
        ]
    }
    s_repo = ServicesRepo(db=mock_db)
    services = s_repo.get_services()
    assert len(services) == 1
    assert services[0]["service_name"] == "Spa"
    assert "get_all_services" in mock_cursor.execute.call_args[0][0]

    # 2. charge_service
    mock_cursor.fetchone.return_value = {
        "add_service_to_booking": {
            "success": True,
            "message": "Service charged",
            "service_log_id": 1,
            "service_total": 10000.0,
        }
    }
    charge_res = s_repo.charge_service(booking_id=101, service_id=1, service_dates=1)
    assert charge_res["success"] is True
    assert "add_service_to_booking" in mock_cursor.execute.call_args[0][0]

    # 3. add_extra_amenity
    mock_cursor.fetchone.return_value = {
        "add_extra_amenity_to_booking": {
            "success": True,
            "message": "Extra amenity added",
        }
    }
    amenity_res = s_repo.add_extra_amenity(booking_id=101, amenity_id=2, quantity=1)
    assert amenity_res["success"] is True
    assert "add_extra_amenity_to_booking" in mock_cursor.execute.call_args[0][0]


def test_billing_repo_calls_db():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor

    # 1. get_all_invoices
    mock_cursor.fetchone.return_value = {
        "get_all_invoices": [
            {
                "invoice_id": "inv-001",
                "booking_id": 101,
                "grand_total": 50000.0,
                "payment_status": "PAID",
            }
        ]
    }
    b_repo = BillingRepo(db=mock_db)
    invoices = b_repo.get_all_invoices()
    assert len(invoices) == 1
    assert invoices[0]["invoice_id"] == "inv-001"
    assert "get_all_invoices" in mock_cursor.execute.call_args[0][0]

    # 2. get_active_stays
    mock_cursor.fetchone.return_value = {
        "get_active_stays": [
            {
                "booking_id": 101,
                "room_number": 201,
                "booking_status": "CHECKED_IN",
            }
        ]
    }
    stays = b_repo.get_active_stays()
    assert len(stays) == 1
    assert stays[0]["room_number"] == 201
    assert "get_active_stays" in mock_cursor.execute.call_args[0][0]

    # 3. checkout_booking
    mock_cursor.fetchone.return_value = {
        "checkout_booking": {
            "success": True,
            "message": "Booking checked out successfully",
            "payment_status": "PAID",
        }
    }
    checkout_res = b_repo.checkout_booking(booking_id=101, payment_method="CREDIT_CARD")
    assert checkout_res["success"] is True
    assert "checkout_booking" in mock_cursor.execute.call_args[0][0]


def test_services_and_billing_service_delegation():
    mock_s_repo = MagicMock(spec=ServicesRepo)
    mock_s_repo.get_services.return_value = [{"service_id": 1}]
    s_service = ServicesService(repo=mock_s_repo)
    assert len(s_service.list_services()) == 1

    mock_b_repo = MagicMock(spec=BillingRepo)
    mock_b_repo.get_active_stays.return_value = [{"booking_id": 99}]
    b_service = BillingService(repo=mock_b_repo)
    assert len(b_service.list_active_stays()) == 1


def test_services_and_billing_endpoints(monkeypatch):
    monkeypatch.setattr(
        ServicesRepo,
        "get_services",
        lambda self: [{"service_id": 1, "service_name": "Spa"}],
    )
    monkeypatch.setattr(
        ServicesRepo,
        "charge_service",
        lambda self, booking_id, service_id, service_dates=1: {
            "success": True,
            "message": "Service charged successfully",
            "service_log_id": 1,
            "service_total": 10000.0,
        },
    )
    monkeypatch.setattr(
        ServicesRepo,
        "add_extra_amenity",
        lambda self, booking_id, amenity_id, quantity=1: {
            "success": True,
            "message": "Extra amenity added successfully",
            "booking_id": booking_id,
            "amenity_id": amenity_id,
            "quantity": quantity,
        },
    )
    monkeypatch.setattr(
        BillingRepo,
        "get_all_invoices",
        lambda self, payment_status=None: [{"invoice_id": "inv-001", "payment_status": "PAID"}],
    )
    monkeypatch.setattr(
        BillingRepo,
        "get_active_stays",
        lambda self: [{"booking_id": 9921, "room_number": 201}],
    )
    monkeypatch.setattr(
        BillingRepo,
        "checkout_booking",
        lambda self, booking_id, payment_method="CREDIT_CARD": {
            "success": True,
            "message": "Booking checked out successfully",
            "booking_id": booking_id,
            "invoice_id": "a0000000-0000-0000-0000-000000000099",
            "payment_status": "PAID",
            "grand_total": 55000.0,
            "amount_paid": 55000.0,
        },
    )
    client = TestClient(app)

    # 1. GET /api/v1/private/services/
    res_s = client.get("/api/v1/private/services/")
    assert res_s.status_code == 200
    assert len(res_s.json()) >= 1

    # 2. POST /api/v1/private/services/charge
    res_charge = client.post(
        "/api/v1/private/services/charge",
        json={"booking_id": 9921, "service_id": 1, "service_dates": 1},
    )
    assert res_charge.status_code == 200
    assert res_charge.json()["success"] is True

    # 3. POST /api/v1/private/services/amenities/extra
    res_extra = client.post(
        "/api/v1/private/services/amenities/extra",
        json={"booking_id": 9921, "amenity_id": 1, "quantity": 2},
    )
    assert res_extra.status_code == 200
    assert res_extra.json()["success"] is True

    # 4. GET /api/v1/private/billing/invoices
    res_inv = client.get("/api/v1/private/billing/invoices")
    assert res_inv.status_code == 200
    assert len(res_inv.json()) >= 1

    # 5. GET /api/v1/private/billing/stays/active
    res_stays = client.get("/api/v1/private/billing/stays/active")
    assert res_stays.status_code == 200
    assert len(res_stays.json()) >= 1

    # 6. POST /api/v1/private/billing/checkout
    res_co = client.post(
        "/api/v1/private/billing/checkout",
        json={"booking_id": 9921, "payment_method": "CREDIT_CARD"},
    )
    assert res_co.status_code == 200
    assert res_co.json()["success"] is True
