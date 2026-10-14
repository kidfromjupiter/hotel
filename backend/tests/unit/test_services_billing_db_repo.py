from unittest.mock import MagicMock
from decimal import Decimal
from uuid import UUID
from app.repositories.billing_repo import BillingRepo
from app.repositories.services_repo import ServicesRepo
from app.services.billing_service import BillingService
from app.services.services_service import ServicesService


def test_services_repo_reads_rows_and_keeps_charge_function():
    mock_db = MagicMock()
    cursor = mock_db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [{"service_id": 1, "service_name": "Spa", "day_rate": 10000}]
    repo = ServicesRepo(db=mock_db)
    assert repo.get_services()[0]["service_name"] == "Spa"
    assert "FROM service_catalogue" in cursor.execute.call_args.args[0]

    cursor.fetchone.return_value = {"add_service_to_booking": {"success": True, "service_log_id": 1}}
    assert repo.charge_service(101, 1)["success"] is True
    assert "add_service_to_booking" in cursor.execute.call_args.args[0]


def test_billing_repo_reads_rows_and_keeps_write_functions():
    mock_db = MagicMock()
    cursor = mock_db.cursor.return_value.__enter__.return_value
    repo = BillingRepo(db=mock_db)

    cursor.fetchall.return_value = [{"invoice_id": "inv-001", "payment_status": "PAID"}]
    assert repo.get_all_invoices()[0]["invoice_id"] == "inv-001"
    assert "FROM billing_summary bs" in cursor.execute.call_args.args[0]
    cursor.fetchall.return_value = [{"booking_id": 101, "booking_status": "CHECKED_IN"}]
    assert repo.get_active_stays()[0]["booking_id"] == 101
    assert "FROM booking b" in cursor.execute.call_args.args[0]

    cursor.fetchone.return_value = {"checkout_booking": {"success": True}}
    assert repo.checkout_booking(101)["success"] is True
    assert "checkout_booking" in cursor.execute.call_args.args[0]
    cursor.fetchone.return_value = {"record_invoice_payment": {"success": True, "new_amount_paid": 125}}
    invoice_id = UUID("a0000000-0000-0000-0000-000000000099")
    assert repo.record_payment(invoice_id, Decimal("25.00"), "Cash")["new_amount_paid"] == 125
    assert cursor.execute.call_args.args[1][1:] == (Decimal("25.00"), "Cash")


def test_services_and_billing_service_delegation():
    mock_s_repo = MagicMock(spec=ServicesRepo)
    mock_s_repo.get_services.return_value = [{"service_id": 1, "service_name": "Spa"}]
    s_service = ServicesService(repo=mock_s_repo)
    assert len(s_service.list_services()) == 1

    mock_b_repo = MagicMock(spec=BillingRepo)
    mock_b_repo.get_active_stays.return_value = [{"booking_id": 99}]
    b_service = BillingService(repo=mock_b_repo)
    assert len(b_service.list_active_stays()) == 1
    invoice_id = UUID("a0000000-0000-0000-0000-000000000099")
    b_service.record_payment(invoice_id, Decimal("25.00"), "Card")
    mock_b_repo.record_payment.assert_called_once_with(invoice_id, Decimal("25.00"), "Card")


def test_services_and_billing_endpoints(monkeypatch, client):
    monkeypatch.setattr(
        ServicesRepo,
        "get_services",
        lambda self: [{"service_id": 1, "service_name": "Spa"}],
    )
    monkeypatch.setattr(
        ServicesRepo,
        "charge_service",
        lambda self, booking_id, service_id, quantity=1: {
            "success": True,
            "message": "Service charged successfully",
            "service_log_id": 1,
            "service_total": 10000.0,
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
        lambda self, booking_id: {
            "success": True,
            "message": "Booking checked out successfully",
            "booking_id": booking_id,
            "invoice_id": "a0000000-0000-0000-0000-000000000099",
            "payment_status": "PAID",
            "grand_total": 55000.0,
            "amount_paid": 55000.0,
        },
    )
    # 1. GET /api/v1/private/services/
    res_s = client.get("/api/v1/private/services/")
    assert res_s.status_code == 200
    assert len(res_s.json()) >= 1

    # 2. POST /api/v1/private/services/charge
    res_charge = client.post(
        "/api/v1/private/services/charge",
        json={"booking_id": 9921, "service_id": 1, "quantity": 1},
    )
    assert res_charge.status_code == 200
    assert res_charge.json()["success"] is True

    # 3. GET /api/v1/private/billing/invoices
    res_inv = client.get("/api/v1/private/billing/invoices")
    assert res_inv.status_code == 200
    assert len(res_inv.json()) >= 1

    # 4. GET /api/v1/private/billing/stays/active
    res_stays = client.get("/api/v1/private/billing/stays/active")
    assert res_stays.status_code == 200
    assert len(res_stays.json()) >= 1

    # 5. POST /api/v1/private/billing/checkout
    res_co = client.post(
        "/api/v1/private/billing/checkout",
        json={"booking_id": 9921, "payment_method": "CREDIT_CARD"},
    )
    assert res_co.status_code == 200
    assert res_co.json()["success"] is True


def test_payment_endpoint_validates_and_returns_recorded_payment(monkeypatch, client):
    invoice_id = "a0000000-0000-0000-0000-000000000099"
    calls = []

    def record(self, received_invoice_id, amount, payment_method):
        calls.append((received_invoice_id, amount, payment_method))
        return {
            "success": True,
            "transaction_id": "b0000000-0000-0000-0000-000000000099",
            "invoice_id": invoice_id,
            "amount": float(amount),
            "payment_method": payment_method,
            "new_amount_paid": 25.0,
            "outstanding_balance": 75.0,
            "payment_status": "PARTIALLY_PAID",
        }

    monkeypatch.setattr(BillingRepo, "record_payment", record)
    path = f"/api/v1/private/billing/invoices/{invoice_id}/payments"

    response = client.post(path, json={"amount": "25.00", "payment_method": "Cash"})
    assert response.status_code == 201
    assert response.json()["outstanding_balance"] == 75.0
    assert calls == [(UUID(invoice_id), Decimal("25.00"), "Cash")]

    for payload in [
        {"amount": "0", "payment_method": "Cash"},
        {"amount": "1.001", "payment_method": "Cash"},
        {"amount": "1.00", "payment_method": "Bank Transfer"},
    ]:
        assert client.post(path, json=payload).status_code == 422
    assert len(calls) == 1


def test_payment_endpoint_rejects_overpayment(monkeypatch, client):
    monkeypatch.setattr(
        BillingRepo,
        "record_payment",
        lambda self, invoice_id, amount, payment_method: {
            "success": False,
            "error_code": "OVERPAYMENT",
            "message": "Payment amount exceeds the outstanding balance.",
        },
    )
    response = client.post(
        "/api/v1/private/billing/invoices/a0000000-0000-0000-0000-000000000099/payments",
        json={"amount": "200.00", "payment_method": "Card"},
    )
    assert response.status_code == 400
    assert "outstanding balance" in response.json()["detail"]
