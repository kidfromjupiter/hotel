import pytest


@pytest.fixture
def sample_bookings(booking_repo):
    booking_repo.save_booking(
        {
            "booking_id": 500101,
            "bookingRef": "SKN-5101",
            "guest_id": 1,
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
        }
    )
    booking_repo.save_booking(
        {
            "booking_id": 500102,
            "bookingRef": "SKN-5102",
            "guest_id": 2,
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
        }
    )
    if booking_repo.db:
        booking_repo.db.commit()


# TODO: This is probably the wrong format to send create booking in.
def test_create_booking_success(client, booking_repo):
    booking_payload = {
        "branch": "colombo",
        "checkIn": "2026-10-15T00:00:00.000Z",
        "checkOut": "2026-10-18T00:00:00.000Z",
        "adults": 2,
        "children": 0,
        "nights": 3,
        "roomId": "deluxe-101",
        "roomType": "Deluxe Room",
        "phone": "+94771234567",
        "totalPrice": 105000,
        "amenityIds": ["airport-pickup"],
        "amenities": [
            {
                "id": "airport-pickup",
                "name": "Airport Pickup",
                "price": 5000,
                "icon": "car",
                "description": "Luxury car transfer",
            }
        ],
    }

    response = client.post("/api/v1/bookings/", json=booking_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["bookingRef"].startswith("SKN-")
    assert "confirmed" in data["message"].lower()

    assert len(booking_repo._bookings) == 1
    saved = booking_repo._bookings[0]
    assert saved["bookingRef"] == data["bookingRef"]
    assert saved["branch"] == "colombo"
    assert saved["roomId"] == "deluxe-101"


def test_create_booking_frontend_alias(client):
    booking_payload = {
        "branch": "colombo",
        "checkIn": "2026-10-15T00:00:00.000Z",
        "checkOut": "2026-10-18T00:00:00.000Z",
        "adults": 2,
        "children": 0,
        "nights": 3,
        "roomId": "deluxe-101",
        "roomType": "Deluxe Room",
        "phone": "+94771234567",
        "totalPrice": 105000,
        "amenityIds": [],
        "amenities": [],
    }
    response = client.post("/api/v1/booking/create", json=booking_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_create_booking_with_name_and_national_id(client):
    payload = {
        "branch": "colombo",
        "checkIn": "2026-10-20T00:00:00.000Z",
        "checkOut": "2026-10-23T00:00:00.000Z",
        "adults": 2,
        "children": 0,
        "nights": 3,
        "roomId": "deluxe-101",
        "roomType": "Deluxe Room",
        "phone": "+94775551234",
        "name": "Sunil Perera",
        "national_id": "198812345678",
        "totalPrice": 75000,
        "amenityIds": [],
        "amenities": [],
    }
    response = client.post("/api/v1/bookings/", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["bookingRef"].startswith("SKN-")



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
    res = client.get("/api/v1/private/bookings/?status=Confirmed")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(b["booking_id"] == 500101 for b in data)


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
    res = client.post(
        "/api/v1/bookings/500101/check-in", json={"check_in_time": "14:30:00"}
    )
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
    booking_repo.save_booking(
        {
            "booking_id": 500103,
            "bookingRef": "SKN-5103",
            "booking_status": "Checked-In",
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
    assert data["booking_status"] == "Checked-Out"
    assert data["checked_out_time"] == "11:00:00"


def test_cancel_booking_success(client, booking_repo):
    booking_repo.save_booking(
        {
            "booking_id": 500104,
            "bookingRef": "SKN-5104",
            "booking_status": "Confirmed",
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
    assert data["booking_status"] == "Cancelled"


def test_cancel_booking_already_checked_in_error(client, sample_bookings):
    # 500102 is Checked-In
    res = client.post("/api/v1/bookings/500102/cancel")
    assert res.status_code == 400
    assert "Cannot cancel a booking that is already Checked-In" in res.json()["detail"]


def test_calculate_bill_with_services_preview(client):
    payload = {
        "branch": "Colombo",
        "room_type": "Deluxe Room",
        "room_number": 201,
        "nights": 3,
        "daily_rate": 22000.0,
        "guest_phone": "0771234567",
        "services": [
            {
                "service_id": 4,
                "service_name": "Spa",
                "quantity": 1,
                "days": 1,
            },
            {
                "service_id": 5,
                "service_name": "Breakfast",
                "quantity": 2,
                "days": 3,
            },
        ],
    }
    res = client.post("/api/v1/bookings/calculate-bill", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PREVIEW_CALCULATED"
    assert data["is_updated"] is False
    assert "room_charges" in data
    assert "services_charges" in data
    assert "taxes" in data
    assert data["room_charges"]["nights"] == 3
    assert data["room_charges"]["daily_rate"] == 22000.0
    assert len(data["services_charges"]["items"]) == 2
    assert data["grand_total"] > 0
    assert data["grand_total"] == round(data["subtotal"] + data["total_tax"], 2)

