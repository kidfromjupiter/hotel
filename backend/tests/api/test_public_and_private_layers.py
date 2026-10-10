def test_public_amenities_route(client):
    res = client.get("/api/v1/public/amenities?branch=colombo")
    assert res.status_code == 200
    data = res.json()
    assert "amenities" in data
    assert len(data["amenities"]) > 0


def test_public_otp_routes(client, otp_service):
    # Test send OTP
    res_send = client.post("/api/v1/public/otp/send", json={"phone": "+94771234567"})
    assert res_send.status_code == 200
    send_data = res_send.json()
    assert send_data["success"] is True

    # Test verify OTP
    code = otp_service._store["+94771234567"][0]
    res_verify = client.post(
        "/api/v1/public/otp/verify",
        json={"phone": "+94771234567", "otp": code},
    )
    assert res_verify.status_code == 200
    assert res_verify.json()["success"] is True



def test_public_create_booking_flow(client, booking_repo):
    booking_payload = {
        "branchId": 1,
        "checkIn": "2026-12-15T00:00:00.000Z",
        "checkOut": "2026-12-18T00:00:00.000Z",
        "adults": 2,
        "children": 0,
        "nights": 3,
        "roomNumber": 201,
        "roomType": "Deluxe Room",
        "phone": "+94771234567",
        "totalPrice": 105000,
        "amenityIds": [],
        "amenities": [],
    }
    res = client.post("/api/v1/public/bookings/", json=booking_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["bookingRef"].startswith("SKN-")


def test_private_booking_staff_operations(client, booking_repo):
    # Seed a booking
    saved = booking_repo.save_booking(
        {
            "booking_id": 99901,
            "guest_id": 1,
            "guest_name": "Test Guest",
            "room_number": 103,
            "branch_id": 1,
            "branch_name": "Colombo",
            "booking_status": "CONFIRMED",
            "start_date": "2027-10-01",
            "end_date": "2027-10-05",
            "grand_total": 50000.0,
            "amount_paid": 50000.0,
            "invoice_status": "PAID",
        }
    )
    if booking_repo.db:
        booking_repo.db.commit()

    # 1. Staff search/list
    res_list = client.get("/api/v1/private/bookings/")
    assert res_list.status_code == 200
    assert any(b["booking_id"] == 99901 for b in res_list.json())

    # 2. Staff get details
    res_detail = client.get("/api/v1/private/bookings/99901")
    assert res_detail.status_code == 200
    assert res_detail.json()["booking_id"] == 99901

    # 3. Staff check-in
    res_checkin = client.post(
        "/api/v1/private/bookings/99901/check-in",
        json={"check_in_time": "14:30:00"},
    )
    assert res_checkin.status_code == 200
    assert res_checkin.json()["booking_status"] == "CHECKED_IN"

    # 4. Staff check-out
    res_checkout = client.post(
        "/api/v1/private/bookings/99901/check-out",
        json={"check_out_time": "11:00:00"},
    )
    assert res_checkout.status_code == 200
    assert res_checkout.json()["booking_status"] == "CHECKED_OUT"


def test_private_reports_routes(client):
    res = client.get("/api/v1/private/reports/occupancy?start_date=2026-10-01&end_date=2026-10-31")
    assert res.status_code == 200
    assert "branches" in res.json()


def test_public_rooms_availability_endpoints(client):
    # Test GET /api/v1/public/rooms/
    res_get = client.get("/api/v1/public/rooms/?branch=colombo&check_in=2026-10-01&check_out=2026-10-05&adults=2&children=0")
    assert res_get.status_code == 200
    assert isinstance(res_get.json(), list)

    # Test POST /api/v1/public/rooms/availability
    post_payload = {
        "branch": "colombo",
        "checkIn": "2026-10-01",
        "checkOut": "2026-10-05",
        "adults": 2,
        "children": 0,
    }
    res_post = client.post("/api/v1/public/rooms/availability", json=post_payload)
    assert res_post.status_code == 200
    data = res_post.json()
    assert "available" in data
    assert "rooms" in data
    assert "message" in data

