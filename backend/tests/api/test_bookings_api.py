import pytest


@pytest.fixture
def sample_bookings(booking_repo):
    booking_repo.save_booking({
        "booking_id": 500101,
        "bookingRef": "SKN-5101",
        "guest_id": 1001,
        "guest_name": "Amal Perera",
        "room_number": 101,
        "branch_id": 1,
        "branch_name": "Colombo",
        "roomId": "standard-room",
        "room_type_id": "STANDARD",
        "booking_status": "Confirmed",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
        "adult_count": 2,
        "children_count": 0,
        "grand_total": 50000.0,
        "amount_paid": 50000.0,
        "invoice_status": "PAID",
    })
    booking_repo.save_booking({
        "booking_id": 500102,
        "bookingRef": "SKN-5102",
        "guest_id": 1002,
        "guest_name": "Kamal Silva",
        "room_number": 201,
        "branch_id": 2,
        "branch_name": "Kandy",
        "roomId": "deluxe-room",
        "room_type_id": "DELUXE",
        "booking_status": "Checked-In",
        "start_date": "2026-10-02",
        "end_date": "2026-10-06",
        "adult_count": 2,
        "children_count": 1,
        "checked_in_time": "14:00:00",
        "grand_total": 84000.0,
        "amount_paid": 0.0,
        "invoice_status": "UNPAID",
    })


def test_list_bookings_all(client, sample_bookings):
    res = client.get("/api/v1/bookings/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2


def test_list_bookings_filtered_by_branch(client, sample_bookings):
    res = client.get("/api/v1/bookings/?branch_id=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["branch_name"] == "Colombo"


def test_list_bookings_filtered_by_status(client, sample_bookings):
    res = client.get("/api/v1/bookings/?status=Checked-In")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["booking_id"] == 500102


def test_get_booking_success(client, sample_bookings):
    res = client.get("/api/v1/bookings/500101")
    assert res.status_code == 200
    data = res.json()
    assert data["booking_id"] == 500101
    assert data["guest"]["name"] == "Amal Perera"
    assert data["room"]["room_number"] == 101
    assert data["booking_status"] == "Confirmed"


def test_get_booking_not_found(client):
    res = client.get("/api/v1/bookings/999999")
    assert res.status_code == 404
    assert "Booking does not exist" in res.json()["detail"]


def test_check_in_success(client, sample_bookings):
    res = client.post("/api/v1/bookings/500101/check-in", json={"check_in_time": "14:30:00"})
    assert res.status_code == 200
    data = res.json()
    assert data["booking_status"] == "Checked-In"
    assert data["checked_in_time"] == "14:30:00"


def test_check_in_invalid_status_error(client, sample_bookings):
    # 500102 is already Checked-In
    res = client.post("/api/v1/bookings/500102/check-in")
    assert res.status_code == 400
    assert "not in 'Confirmed' status" in res.json()["detail"]


def test_check_out_unpaid_balance_error(client, sample_bookings):
    # 500102 has amount_paid: 0.0 < grand_total: 84000.0
    res = client.post("/api/v1/bookings/500102/check-out")
    assert res.status_code == 400
    assert "Outstanding unpaid balance exists" in res.json()["detail"]


def test_check_out_success_when_paid(client, booking_repo):
    booking_repo.save_booking({
        "booking_id": 500103,
        "bookingRef": "SKN-5103",
        "booking_status": "Checked-In",
        "grand_total": 40000.0,
        "amount_paid": 40000.0,
    })
    res = client.post("/api/v1/bookings/500103/check-out", json={"check_out_time": "11:00:00"})
    assert res.status_code == 200
    data = res.json()
    assert data["booking_status"] == "Checked-Out"
    assert data["checked_out_time"] == "11:00:00"


def test_cancel_booking_success(client, sample_bookings):
    res = client.post("/api/v1/bookings/500101/cancel")
    assert res.status_code == 200
    data = res.json()
    assert data["booking_status"] == "Cancelled"


def test_cancel_booking_already_checked_in_error(client, sample_bookings):
    # 500102 is Checked-In
    res = client.post("/api/v1/bookings/500102/cancel")
    assert res.status_code == 400
    assert "Cannot cancel a booking that is already Checked-In" in res.json()["detail"]
