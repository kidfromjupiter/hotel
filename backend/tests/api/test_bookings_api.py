import pytest


@pytest.fixture
def sample_bookings(booking_repo):
    booking_repo.save_booking(
        {
            "booking_id": 500101,
            "guest_id": 1,
            "guest_name": "Amal Perera",
            "room_number": 101,
            "branch_id": 1,
            "branch_name": "Colombo",
            "room_type_id": "STANDARD",
            "booking_status": "CONFIRMED",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
            "adult_count": 2,
            "children_count": 0,
            "grand_total": 50000.0,
            "amount_paid": 50000.0,
            "invoice_status": "PAID",
        }
    )
    booking_repo.save_booking(
        {
            "booking_id": 500102,
            "guest_id": 2,
            "guest_name": "Kamal Silva",
            "room_number": 201,
            "branch_id": 2,
            "branch_name": "Kandy",
            "room_type_id": "DELUXE",
            "booking_status": "CHECKED_IN",
            "start_date": "2026-10-02",
            "end_date": "2026-10-06",
            "adult_count": 2,
            "children_count": 1,
            "checked_in_time": "14:00:00",
            "grand_total": 84000.0,
            "amount_paid": 0.0,
        }
    )
    if booking_repo.db:
        booking_repo.db.commit()


def test_create_booking_success(client, booking_repo):
    booking_payload = {
        "branchId": 1,
        "checkIn": "2026-10-15T00:00:00.000Z",
        "checkOut": "2026-10-18T00:00:00.000Z",
        "adults": 2,
        "children": 0,
        "nights": 3,
        "roomNumber": 201,
        "roomType": "Deluxe Room",
        "phone": "+94771234567",
        "totalPrice": 105000,
    }

    response = client.post("/api/v1/bookings/", json=booking_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["bookingRef"].startswith("SKN-")
    assert "confirmed" in data["message"].lower()

    if booking_repo.db:
        with booking_repo.db.cursor() as cursor:
            cursor.execute(
                "SELECT booking_id, booking_ref, room_number, branch_id "
                "FROM booking WHERE booking_ref = %s",
                (data["bookingRef"],),
            )
            booking_id, booking_ref, room_number, branch_id = cursor.fetchone()
            assert booking_ref == f"SKN-{booking_id}"
            assert (branch_id, room_number) == (1, 201)


def test_create_booking_frontend_alias(client):
    booking_payload = {
        "branchId": 1,
        "checkIn": "2026-11-15T00:00:00.000Z",
        "checkOut": "2026-11-18T00:00:00.000Z",
        "adults": 2,
        "children": 0,
        "nights": 3,
        "roomNumber": 201,
        "roomType": "Deluxe Room",
        "phone": "+94771234567",
        "totalPrice": 105000,
    }
    response = client.post("/api/v1/booking/create", json=booking_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_create_booking_rejects_unknown_branch_room_pair(client):
    response = client.post(
        "/api/v1/bookings/",
        json={
            "branchId": 999,
            "roomNumber": 201,
            "checkIn": "2026-11-15",
            "checkOut": "2026-11-18",
            "adults": 2,
            "children": 0,
            "nights": 3,
            "roomType": "Deluxe Room",
            "phone": "+94771234567",
            "totalPrice": 105000,
        },
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"] == "The selected room does not exist at this branch."
    )


def test_list_bookings_all(client, sample_bookings):
    res = client.get("/api/v1/private/bookings/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2


def test_list_bookings_filtered_by_branch(client, sample_bookings):
    res = client.get("/api/v1/private/bookings/?branch_id=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(b["booking_id"] == 500101 for b in data)


def test_list_bookings_filtered_by_status(client, sample_bookings):
    res = client.get("/api/v1/private/bookings/?status=CONFIRMED")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(b["booking_id"] == 500101 for b in data)


def test_get_booking_success(client, sample_bookings):
    res = client.get("/api/v1/bookings/500101")
    assert res.status_code == 200
    data = res.json()
    assert data["booking_id"] == 500101
    assert data["booking_ref"] == "SKN-500101"
    assert data["guest"]["name"] == "Amal Perera"
    assert data["room"]["room_number"] == 101
    assert data["booking_status"] == "CONFIRMED"


def test_receptionist_lookup_uses_stored_booking_reference(client, sample_bookings):
    res = client.post(
        "/api/v1/private/bookings/verify-otp",
        json={"otp": "SKN-500101"},
    )
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["booking"]["bookingReference"] == "SKN-500101"


def test_get_booking_not_found(client):
    res = client.get("/api/v1/bookings/999999")
    assert res.status_code == 404
    assert "Booking does not exist" in res.json()["detail"]


def test_check_in_success(client, sample_bookings):
    res = client.post(
        "/api/v1/bookings/500101/check-in", json={"check_in_time": "14:30:00"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["booking_status"] == "CHECKED_IN"
    assert data["checked_in_time"] == "14:30:00"


def test_check_in_invalid_status_error(client, sample_bookings):
    # 500102 is already CHECKED_IN
    res = client.post("/api/v1/bookings/500102/check-in")
    assert res.status_code == 400
    assert "not in 'CONFIRMED' status" in res.json()["detail"]


def test_check_out_unpaid_balance_error(client, sample_bookings):
    # 500102 has amount_paid: 0.0 < grand_total: 84000.0
    res = client.post("/api/v1/bookings/500102/check-out")
    assert res.status_code == 400
    assert "Outstanding unpaid balance exists" in res.json()["detail"]


def test_check_out_success_when_paid(client, booking_repo):
    booking_repo.save_booking(
        {
            "booking_id": 500103,
            "booking_status": "CHECKED_IN",
            "grand_total": 40000.0,
            "amount_paid": 40000.0,
            "guest_id": 1,
            "room_number": 101,
            "branch_id": 1,
        }
    )
    if booking_repo.db:
        booking_repo.db.commit()
    res = client.post(
        "/api/v1/bookings/500103/check-out", json={"check_out_time": "11:00:00"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["booking_status"] == "CHECKED_OUT"
    assert data["checked_out_time"] == "11:00:00"


def test_cancel_booking_success(client, booking_repo):
    booking_repo.save_booking(
        {
            "booking_id": 500104,
            "booking_status": "CONFIRMED",
            "guest_id": 1,
            "room_number": 101,
            "branch_id": 1,
        }
    )
    if booking_repo.db:
        booking_repo.db.commit()
    res = client.post("/api/v1/bookings/500104/cancel")
    assert res.status_code == 200
    data = res.json()
    assert data["booking_status"] == "CANCELLED"


def test_cancel_booking_already_checked_in_error(client, sample_bookings):
    # 500102 is CHECKED_IN
    res = client.post("/api/v1/bookings/500102/cancel")
    assert res.status_code == 400
    assert "Cannot cancel a booking that is already CHECKED_IN" in res.json()["detail"]
