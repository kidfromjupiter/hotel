from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder

from app.phone import normalize_phone
from app.repositories.booking_repo import BookingRepository
from app.repositories.rooms_repo import RoomsRepo
from app.schemas.bookings import (
    AdminReservationListItem,
    BookingDetailResponse,
    BookingListItem,
    CancelBookingResponse,
    CheckInResponse,
    CheckOutResponse,
    ExtendStayResponse,
    GuestProfileSummary,
    RoomSummary,
    ServiceChargeItem,
)


class BookingService:
    def __init__(self, *, booking_repo: BookingRepository, rooms_repo: Optional[RoomsRepo] = None):
        self.booking_repo = booking_repo
        self.rooms_repo = rooms_repo

    def create_booking(self, request: Any, guest_token: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if hasattr(request, "model_dump"):
            booking_dict = request.model_dump()
        elif isinstance(request, dict):
            booking_dict = dict(request)
        else:
            booking_dict = dict(request)

        booking_dict["branch_id"] = booking_dict.pop("branchId")
        booking_dict["room_number"] = booking_dict.pop("roomNumber")

        guest_id = guest_token.get("guest_id") if guest_token else None
        pricing = self.booking_repo.get_room_pricing(
            booking_dict["branch_id"], booking_dict["room_number"], guest_id
        )
        if pricing is None:
            raise HTTPException(
                status_code=404,
                detail="The selected room does not exist at this branch.",
            )

        try:
            check_in = date.fromisoformat(booking_dict["checkIn"])
            check_out = date.fromisoformat(booking_dict["checkOut"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="Enter valid check-in and check-out dates.")
        nights = (check_out - check_in).days
        if nights < 1:
            raise HTTPException(status_code=422, detail="Check-out must be after check-in.")
        if booking_dict["adults"] < 1 or booking_dict["children"] < 0:
            raise HTTPException(status_code=422, detail="Enter a valid number of guests.")
        if booking_dict["adults"] + booking_dict["children"] > pricing["capacity"]:
            raise HTTPException(status_code=422, detail="The selected room cannot fit all guests.")
        if pricing["room_status"] == "MAINTENANCE":
            raise HTTPException(status_code=409, detail="The selected room is under maintenance.")

        discount = Decimal(str(pricing["room_discount_percentage"]))
        daily_rate = Decimal(str(pricing["daily_rate"]))
        booking_dict["grand_total"] = (
            daily_rate * nights * (Decimal("1") - discount / Decimal("100"))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        booking_dict["start_date"] = check_in
        booking_dict["end_date"] = check_out
        booking_dict.pop("totalPrice", None)
        if guest_id is not None:
            booking_dict["guest_id"] = guest_id

        saved = self.booking_repo.save_booking(booking_dict)
        return {
            "success": True,
            "bookingRef": saved["booking_ref"],
            "totalPrice": float(booking_dict["grand_total"]),
            "message": "Your reservation has been confirmed successfully!",
        }

    def check_availability(self, request: Any) -> Dict[str, Any]:
        """Calculates room availability from room repository rows."""
        adults = getattr(request, "adults", 1)
        children = getattr(request, "children", 0)
        branch = getattr(request, "branch", "colombo")
        check_in_raw = getattr(request, "checkIn", None) or getattr(request, "check_in", None) or "2026-10-01"
        check_out_raw = getattr(request, "checkOut", None) or getattr(request, "check_out", None) or "2026-10-02"

        # Calculate nights
        try:
            if isinstance(check_in_raw, (date, datetime)):
                d_in = check_in_raw if isinstance(check_in_raw, date) else check_in_raw.date()
            else:
                d_in = datetime.fromisoformat(str(check_in_raw).replace("Z", "+00:00")).date()

            if isinstance(check_out_raw, (date, datetime)):
                d_out = check_out_raw if isinstance(check_out_raw, date) else check_out_raw.date()
            else:
                d_out = datetime.fromisoformat(str(check_out_raw).replace("Z", "+00:00")).date()

            nights = (d_out - d_in).days
        except Exception:
            d_in = date.today()
            d_out = date.today()
            nights = 1

        if nights < 1:
            nights = 1

        if self.rooms_repo is None:
            raise RuntimeError("Rooms repository is unavailable")
        raw_rooms = self.rooms_repo.get_rooms(
            check_in=d_in,
            check_out=d_out,
            branch=branch,
            children=children,
            adults=adults,
        )

        available_rooms = []
        for room in raw_rooms:
            r_data = dict(room)
            r_data["branch_name"] = (r_data.get("branch_name") or "").title()
            price_per_night = (
                r_data.get("pricePerNight")
                or r_data.get("price_per_night")
                or r_data.get("daily_rate")
                or 25000
            )
            r_data["nights"] = nights
            r_data["price_per_night"] = float(price_per_night)
            r_data["pricePerNight"] = float(price_per_night)
            r_data["totalPrice"] = float(price_per_night) * nights
            if "id" not in r_data and "room_number" in r_data:
                r_data["id"] = f"room-{r_data['room_number']}"
            if "name" not in r_data:
                r_data["name"] = f"Room {r_data.get('room_number', '')} ({r_data.get('room_type_id', 'STANDARD')})"
            available_rooms.append(r_data)

        return jsonable_encoder({
            "available": len(available_rooms) > 0,
            "rooms": available_rooms,
            "message": "Rooms available"
            if available_rooms
            else "No rooms available for the selected dates.",
        })

    # ── Booking Lifecycle & Management Methods ──

    def list_bookings(
        self,
        branch_id: Optional[int] = None,
        guest_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[BookingListItem]:
        bookings = self.booking_repo.list_all_bookings(
            branch_id=branch_id,
            guest_id=guest_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )
        results: List[BookingListItem] = []

        for b in bookings:
            results.append(
                BookingListItem(
                    booking_id=b.get("booking_id", 0),
                    booking_ref=b["booking_ref"],
                    guest_id=b.get("guest_id"),
                    guest_name=b.get("guest_name") or "Guest",
                    room_number=b.get("room_number", 101),
                    branch_name=(b.get("branch_name") or "Colombo").title(),
                    booking_status=b.get("booking_status", "CONFIRMED"),
                    start_date=str(b.get("start_date") or b.get("checkIn", "")[:10]),
                    end_date=str(b.get("end_date") or b.get("checkOut", "")[:10]),
                    guest_phone=b.get("guest_phone", "N/A"),
                    is_member=b.get("is_member", False),
                )
            )
        return results

    def list_guest_bookings(self, guest_id: int) -> List[Dict[str, Any]]:
        rows = self.booking_repo.list_all_bookings(guest_id=guest_id)
        return jsonable_encoder([
            {**row, "guest_name": row.get("guest_name") or "Guest",
             "branch_name": (row.get("branch_name") or "Colombo").title(),
             "invoice_status": row.get("invoice_status") or "UNPAID",
             "grand_total": row.get("grand_total") or 0,
             "amount_paid": row.get("amount_paid") or 0}
            for row in rows
        ])

    def get_admin_reservations_list(
        self,
        branch_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[AdminReservationListItem]:
        bookings = self.booking_repo.get_admin_reservations_list(
            branch_id=branch_id,
            status=status,
        )
        results: List[AdminReservationListItem] = []

        for b in bookings:
            results.append(
                AdminReservationListItem(
                    booking_id=b.get("booking_id", 0),
                    booking_ref=b["booking_ref"],
                    guest_id=b.get("guest_id"),
                    guest_name=b.get("guest_name") or "Unknown Guest",
                    guest_contact=b.get("guest_contact"),
                    room_number=b.get("room_number", 0),
                    room_type_id=b.get("room_type_id"),
                    branch_id=b.get("branch_id"),
                    branch_name=(b.get("branch_name") or "Unknown").title(),
                    booking_status=b.get("booking_status", "CONFIRMED"),
                    start_date=str(b.get("start_date") or ""),
                    end_date=str(b.get("end_date") or ""),
                    nights=b.get("nights", 1),
                    adult_count=b.get("adult_count", 1),
                    children_count=b.get("children_count", 0),
                    total_room_charges=float(b.get("total_room_charges", 0.0)),
                    total_service_charges=float(b.get("total_service_charges", 0.0)),
                    total_tax_amount=float(b.get("total_tax_amount", 0.0)),
                    grand_total=float(b.get("grand_total", 0.0)),
                    amount_paid=float(b.get("amount_paid", 0.0)),
                    balance_amount=float(b.get("balance_amount", 0.0)),
                    invoice_status=b.get("invoice_status") or "UNPAID",
                    payment_method=b.get("payment_method", "NONE"),
                )
            )
        return results

    def get_booking_by_id(self, booking_id: int) -> BookingDetailResponse:
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        services = [
            ServiceChargeItem(
                service_name=s.get("service_name") or "Service",
                service_dates=s.get("service_dates", 1),
                service_total=float(s.get("service_total", 0.0)),
            )
            for s in self.booking_repo.get_service_charges(booking_id)
        ]

        return BookingDetailResponse(
            booking_id=b["booking_id"],
            booking_ref=b["booking_ref"],
            invoice_id=str(b["invoice_id"]) if b.get("invoice_id") else None,
            guest=GuestProfileSummary(
                guest_id=b.get("guest_id", 1001),
                name=b.get("guest_name") or "Guest",
            ),
            room=RoomSummary(
                room_number=b.get("room_number", 101),
                branch_name=(b.get("branch_name") or "Colombo").title(),
                room_type_id=b.get("room_type_id") or "STANDARD",
            ),
            booking_status=b.get("booking_status", "CONFIRMED"),
            start_date=str(b.get("start_date") or b.get("checkIn", "")[:10]),
            end_date=str(b.get("end_date") or b.get("checkOut", "")[:10]),
            checked_in_time=str(b.get("checked_in_time")) if b.get("checked_in_time") else None,
            checked_out_time=str(b.get("checked_out_time")) if b.get("checked_out_time") else None,
            adult_count=b.get("adult_count", 2),
            children_count=b.get("children_count", 0),
            service_charges=services,
            invoice_status=b.get("invoice_status") or "UNPAID",
            grand_total=float(b.get("grand_total", 0.0)),
            amount_paid=float(b.get("amount_paid", 0.0)),
            total_room_charges=float(b.get("total_room_charges", 0.0)),
            total_service_charges=float(b.get("total_service_charges", 0.0)),
            total_tax_amount=float(b.get("total_tax_amount", 0.0)),
        )

    def get_booking_record(self, booking_id: int) -> Dict[str, Any]:
        booking = self.booking_repo.find_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking does not exist.")
        return booking

    def extend_stay(
        self, booking_id: int, new_check_out_date: date
    ) -> ExtendStayResponse:
        result = self.booking_repo.extend_stay(booking_id, new_check_out_date)
        if not result.get("success"):
            error_code = result.get("error_code")
            status_code = 404 if error_code == "NOT_FOUND" else 409 if error_code == "OVERLAP" else 400
            raise HTTPException(
                status_code=status_code,
                detail=result.get("message", "The stay could not be extended."),
            )
        return ExtendStayResponse(**result)

    def check_in(
        self, booking_id: int, check_in_time: Optional[str] = None
    ) -> CheckInResponse:
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status != "CONFIRMED":
            raise HTTPException(
                status_code=400,
                detail=f"Booking is not in 'CONFIRMED' status (current status: {current_status}).",
            )

        in_time = check_in_time or datetime.now().strftime("%H:%M:%S")
        updated = self.booking_repo.update_booking(
            booking_id,
            {"booking_status": "CHECKED_IN", "checked_in_time": in_time},
        )
        if not updated:
            raise HTTPException(status_code=409, detail="Booking status changed before check-in.")
        return CheckInResponse(
            booking_id=booking_id,
            booking_status="CHECKED_IN",
            checked_in_time=in_time,
        )



    def cancel_booking(self, booking_id: int) -> CancelBookingResponse:
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status in ("CHECKED_IN", "CHECKED_OUT"):
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel a booking that is already CHECKED_IN or CHECKED_OUT.",
            )

        updated = self.booking_repo.update_booking(booking_id, {"booking_status": "CANCELLED"})
        if not updated:
            raise HTTPException(status_code=409, detail="Booking status changed before cancellation.")
        return CancelBookingResponse(
            booking_id=booking_id,
            booking_status="CANCELLED",
        )
    def add_service_to_booking(self, booking_id: int, payload):
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(
                status_code=404,
                detail="Booking does not exist.",
            )

        current_status = b.get("booking_status", "")
        if current_status not in ("CONFIRMED", "CHECKED_IN"):
            raise HTTPException(
                status_code=400,
                detail="Can only add services to active stays.",
            )

        service_id = getattr(payload, "service_id", None) or 1
        service_dates = getattr(payload, "service_dates", None) or 1

        self.booking_repo.add_service_to_booking(
            booking_id, service_id, service_dates
        )
        return self.get_booking_by_id(booking_id)

    def get_pending_booking_by_id(self, booking_id: int):
        b = self.booking_repo.find_booking_by_id(booking_id)
        if b and b.get("booking_status") in ["CONFIRMED", "CHECKED_IN"]:
            return {
                "success": True,
                "booking": {
                    "id": b.get("booking_id", "TBD"),
                    "bookingReference": b["booking_ref"],
                    "guestName": b.get("guest_name", "Guest"),
                    "phone": b.get("guest_phone", ""),
                    "roomType": b.get("room_type_id", "Standard Room"),
                    "roomNumber": b.get("room_number", "TBD"),
                    "checkIn": b.get("start_date") or b.get("checkIn", "")[:10],
                    "checkOut": b.get("end_date") or b.get("checkOut", "")[:10],
                    "status": b.get("booking_status", "CONFIRMED")
                }
            }
        return {"success": False, "message": "Booking not found or not in pending state."}

    def get_pending_booking_by_ref(self, booking_ref: str):
        b = self.booking_repo.find_booking_by_ref(booking_ref)
        if b and b.get("booking_status") in ["CONFIRMED", "CHECKED_IN"]:
            return {
                "success": True,
                "booking": {
                    "id": b["booking_id"],
                    "bookingReference": b["booking_ref"],
                    "guestName": b.get("guest_name", "Guest"),
                    "phone": b.get("guest_phone", ""),
                    "roomType": b.get("room_type_id", "Standard Room"),
                    "roomNumber": b["room_number"],
                    "checkIn": b.get("start_date"),
                    "checkOut": b.get("end_date"),
                    "status": b.get("booking_status", "CONFIRMED"),
                },
            }
        return {"success": False, "message": "Booking not found or not in pending state."}

    def get_pending_booking_by_phone(self, phone: str):
        bookings = self.booking_repo.list_all_bookings()
        normalized = normalize_phone(phone)
        for b in bookings:
            # We are using .get() because b is a dictionary
            if (
                normalized
                and normalize_phone(b.get("guest_phone") or "") == normalized
                and b.get("booking_status") == "CONFIRMED"
            ):
                # Returning the exact structure the frontend expects
                return {
                    "success": True,
                    "booking": {
                        "id": b.get("booking_id", "TBD"),
                        "bookingReference": b["booking_ref"],
                        "guestName": b.get("guest_name", "Guest"),
                        "phone": b.get("guest_phone", phone),
                        "roomType": b.get("room_type_id", "Standard Room"),
                        "roomNumber": b.get("room_number", "TBD"),
                        "checkIn": b.get("start_date") or b.get("checkIn", "")[:10],
                        "checkOut": b.get("end_date") or b.get("checkOut", "")[:10],
                        "status": b.get("booking_status", "CONFIRMED")
                    }
                }

        # If the loop finishes without finding a match:
        return {"success": False, "message": "Invalid OTP or booking not found."}
