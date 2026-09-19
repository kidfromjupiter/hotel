# ─────────────────────────────────────────────
# 1. Check Room Availability Tests
# ─────────────────────────────────────────────


def test_check_availability_success(client):
    payload = {
        "branch": "colombo",
        "checkIn": "2026-10-15T00:00:00.000Z",
        "checkOut": "2026-10-18T00:00:00.000Z",
        "adults": 2,
        "children": 0,
    }
    response = client.post("/api/rooms/availability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert len(data["rooms"]) >= 1

    room = data["rooms"][0]
    assert "id" in room
    assert "name" in room
    assert "pricePerNight" in room
    assert room["nights"] == 3
    assert room["totalPrice"] == room["pricePerNight"] * 3
    assert room["maxCapacity"] >= 2


def test_check_availability_capacity_exceeded(client):
    payload = {
        "branch": "colombo",
        "checkIn": "2026-10-15T00:00:00.000Z",
        "checkOut": "2026-10-18T00:00:00.000Z",
        "adults": 8,
        "children": 2,
    }
    response = client.post("/api/rooms/availability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
    assert len(data["rooms"]) == 0
    assert "Maximum capacity" in data["message"]


def test_check_availability_filters_overlapping_bookings(client, booking_repo):
    booking_repo.save_booking(
        {
            "bookingRef": "SKN-1111",
            "branch": "colombo",
            "start_date": "2026-10-15",
            "end_date": "2026-10-18",
            "roomId": "standard-room",
        }
    )

    payload = {
        "branch": "colombo",
        "checkIn": "2026-10-16T00:00:00.000Z",
        "checkOut": "2026-10-19T00:00:00.000Z",
        "adults": 2,
        "children": 0,
    }
    response = client.post("/api/rooms/availability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    room_ids = [r["id"] for r in data["rooms"]]
    assert "standard-room" not in room_ids
    assert "deluxe-room" in room_ids


# ─────────────────────────────────────────────
# 2. Amenities Endpoint Tests
# ─────────────────────────────────────────────


def test_get_amenities_colombo(client):
    response = client.get("/api/amenities?branch=colombo")
    assert response.status_code == 200
    data = response.json()
    assert "amenities" in data
    assert len(data["amenities"]) >= 2
    item = data["amenities"][0]
    assert "id" in item
    assert "name" in item
    assert "price" in item
    assert "icon" in item


def test_get_amenities_kandy(client):
    response = client.get("/api/amenities?branch=kandy")
    assert response.status_code == 200
    data = response.json()
    assert any(
        "tea" in a["id"] or "tea" in a["name"].lower() for a in data["amenities"]
    )


# ─────────────────────────────────────────────
# 3 & 4. OTP Send & Verify Tests
# ─────────────────────────────────────────────


def test_otp_send_and_verify_flow(client, otp_service):
    phone = "+94771234567"

    send_res = client.post("/api/otp/send", json={"phone": phone})
    assert send_res.status_code == 200
    assert send_res.json()["success"] is True

    stored_record = otp_service._store.get(phone)
    assert stored_record is not None
    otp_code = stored_record[0]

    bad_verify = client.post("/api/otp/verify", json={"phone": phone, "otp": "000000"})
    assert bad_verify.status_code == 400
    assert bad_verify.json()["success"] is False
    assert "Invalid or expired OTP" in bad_verify.json()["message"]

    good_verify = client.post("/api/otp/verify", json={"phone": phone, "otp": otp_code})
    assert good_verify.status_code == 200
    assert good_verify.json()["success"] is True
    assert "verified successfully" in good_verify.json()["message"]


# ─────────────────────────────────────────────
# 5. Create Final Booking Tests
# ─────────────────────────────────────────────


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

    response = client.post("/api/booking/create", json=booking_payload)
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
