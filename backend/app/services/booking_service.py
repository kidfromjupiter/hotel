from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request

from app.repositories.booking_repo import BookingRepository
from app.schemas.bookings import (
    AdminReservationListItem,
    BookingDetailResponse,
    BookingListItem,
    CancelBookingResponse,
    CheckInResponse,
    CheckOutResponse,
    GuestProfileSummary,
    RoomSummary,
    ServiceChargeItem,
)


class BookingService:
    def __init__(self, *, booking_repo: BookingRepository):
        self.booking_repo = booking_repo

    def get_amenities(self, branch: str = "colombo") -> Dict[str, Any]:
        branch_clean = branch.lower() if branch else "colombo"
        if self.booking_repo.db is not None:
            try:
                from psycopg2.extras import RealDictCursor
                with self.booking_repo.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT get_branch_amenities(%s)", (branch_clean,))
                    row = cursor.fetchone()
                    if row and "get_branch_amenities" in row and row["get_branch_amenities"]:
                        return {"amenities": row["get_branch_amenities"]}
            except Exception:
                pass
        return {"amenities": []}

    def create_booking(self, request: Any, guest_token: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if hasattr(request, "model_dump"):
            booking_dict = request.model_dump()
        elif isinstance(request, dict):
            booking_dict = dict(request)
        else:
            booking_dict = dict(request)

        # Apply membership discounts if token is present
        if guest_token:
            discount = guest_token.get("discount_percent", 0)
            if discount > 0:
                original_price = booking_dict.get("totalPrice", 0.0)
                booking_dict["totalPrice"] = round(original_price * (1 - (discount / 100.0)), 2)
            
            # Auto-assign guest_id if they are logged in
            if guest_token.get("guest_id") and not booking_dict.get("guest_id"):
                booking_dict["guest_id"] = guest_token.get("guest_id")

        saved = self.booking_repo.save_booking(booking_dict)
        return {
            "success": True,
            "bookingRef": saved["bookingRef"],
            "message": "Your reservation has been confirmed successfully!",
        }

    def check_availability(self, request: Any) -> Dict[str, Any]:
        """Calculates room availability using database function get_available_rooms."""
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

        # Query available rooms from database function
        raw_rooms = self.booking_repo.get_available_rooms(
            check_in=d_in,
            check_out=d_out,
            branch=branch,
            children=children,
            adults=adults,
        )

        available_rooms = []
        for room in raw_rooms:
            r_data = dict(room)
            price_per_night = (
                r_data.get("pricePerNight")
                or r_data.get("price_per_night")
                or r_data.get("daily_rate")
                or 25000
            )
            r_data["nights"] = nights
            r_data["pricePerNight"] = price_per_night
            r_data["totalPrice"] = price_per_night * nights
            if "id" not in r_data and "room_number" in r_data:
                r_data["id"] = f"room-{r_data['room_number']}"
            if "name" not in r_data:
                r_data["name"] = f"Room {r_data.get('room_number', '')} ({r_data.get('room_type_id', 'STANDARD')})"
            available_rooms.append(r_data)

        return {
            "available": len(available_rooms) > 0,
            "rooms": available_rooms,
            "message": "Rooms available"
            if available_rooms
            else "No rooms available for the selected dates.",
        }

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
                    guest_name=b.get("guest_name", "Guest"),
                    room_number=b.get("room_number", 101),
                    branch_name=b.get("branch_name", "Colombo"),
                    booking_status=b.get("booking_status", "CONFIRMED"),
                    start_date=str(b.get("start_date") or b.get("checkIn", "")[:10]),
                    end_date=str(b.get("end_date") or b.get("checkOut", "")[:10]),
                    guest_phone=b.get("guest_phone", "N/A"),
                    is_member=b.get("is_member", False),
                )
            )
        return results

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
                    booking_ref=b.get("booking_ref"),
                    guest_id=b.get("guest_id"),
                    guest_name=b.get("guest_name", "Unknown Guest"),
                    guest_contact=b.get("guest_contact"),
                    room_number=b.get("room_number", 0),
                    room_type_id=b.get("room_type_id"),
                    branch_id=b.get("branch_id"),
                    branch_name=b.get("branch_name", "Unknown"),
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
                    invoice_status=b.get("invoice_status", "UNPAID"),
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
                service_name=s.get("service_name", "Service"),
                service_dates=s.get("service_dates", 1),
                service_total=float(s.get("service_total", 0.0)),
            )
            for s in b.get("service_charges", [])
        ]

        return BookingDetailResponse(
            booking_id=b["booking_id"],
            guest=GuestProfileSummary(
                guest_id=b.get("guest_id", 1001),
                name=b.get("guest_name", "Guest"),
            ),
            room=RoomSummary(
                room_number=b.get("room_number", 101),
                branch_name=b.get("branch_name", "Colombo"),
                room_type_id=b.get("room_type_id", "STANDARD"),
            ),
            booking_status=b.get("booking_status", "CONFIRMED"),
            start_date=str(b.get("start_date") or b.get("checkIn", "")[:10]),
            end_date=str(b.get("end_date") or b.get("checkOut", "")[:10]),
            checked_in_time=str(b.get("checked_in_time")) if b.get("checked_in_time") else None,
            checked_out_time=str(b.get("checked_out_time")) if b.get("checked_out_time") else None,
            adult_count=b.get("adult_count", 2),
            children_count=b.get("children_count", 0),
            service_charges=services,
            invoice_status=b.get("invoice_status", "PENDING"),
            grand_total=float(b.get("grand_total", 0.0)),
            amount_paid=float(b.get("amount_paid", 0.0)),
        )

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
        self.booking_repo.update_booking(
            booking_id,
            {"booking_status": "CHECKED_IN", "checked_in_time": in_time},
        )
        return CheckInResponse(
            booking_id=booking_id,
            booking_status="CHECKED_IN",
            checked_in_time=in_time,
        )

    def check_out(
        self, booking_id: int, check_out_time: Optional[str] = None
    ) -> CheckOutResponse:
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status != "CHECKED_IN":
            raise HTTPException(
                status_code=400,
                detail=f"Booking is not in 'CHECKED_IN' status (current status: {current_status}).",
            )

        grand_total = float(b.get("grand_total", 0.0))
        amount_paid = float(b.get("amount_paid", 0.0))
        if amount_paid < grand_total:
            outstanding = grand_total - amount_paid
            raise HTTPException(
                status_code=400,
                detail=f"Outstanding unpaid balance exists: ${outstanding:,.2f}. Full payment required before checkout.",
            )

        out_time = check_out_time or datetime.now().strftime("%H:%M:%S")
        self.booking_repo.update_booking(
            booking_id,
            {"booking_status": "CHECKED_OUT", "checked_out_time": out_time},
        )
        return CheckOutResponse(
            booking_id=booking_id,
            booking_status="CHECKED_OUT",
            checked_out_time=out_time,
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

        self.booking_repo.update_booking(booking_id, {"booking_status": "CANCELLED"})
        return CancelBookingResponse(
            booking_id=booking_id,
            booking_status="CANCELLED",
        )
    def add_service_to_booking(self, booking_id: int, payload):
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")
            
        current_status = b.get("booking_status", "")
        if current_status not in ("CONFIRMED", "CHECKED_IN"):
            raise HTTPException(status_code=400, detail="Can only add services to active stays.")
            
        if self.booking_repo.db is not None:
            try:
                from psycopg2.extras import RealDictCursor
                with self.booking_repo.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    service_id = getattr(payload, "service_id", None) or 1
                    service_dates = getattr(payload, "service_dates", None) or 1
                    cursor.execute(
                        "SELECT add_service_to_booking(%s, %s, %s)",
                        (booking_id, service_id, service_dates),
                    )
                self.booking_repo.db.commit()
            except Exception:
                pass
        return self.get_booking_by_id(booking_id)

    def get_pending_booking_by_id(self, booking_id: int):
        b = self.booking_repo.find_booking_by_id(booking_id)
        if b and b.get("booking_status") in ["CONFIRMED", "CHECKED_IN"]:
            return {
                "success": True,
                "booking": {
                    "id": b.get("booking_id", "TBD"),
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

    def get_pending_booking_by_phone(self, phone: str):
        bookings = self.booking_repo.list_all_bookings()
        for b in bookings:
            # We are using .get() because b is a dictionary
            if b.get("guest_phone") == phone and b.get("booking_status") == "CONFIRMED":
                # Returning the exact structure the frontend expects
                return {
                    "success": True,
                    "booking": {
                        "id": b.get("booking_id", "TBD"),
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
