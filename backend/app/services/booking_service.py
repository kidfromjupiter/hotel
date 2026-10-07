from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request

from app.repositories.booking_repo import BookingRepository
from app.schemas.bookings import (
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
        return {"amenities": self.booking_repo.get_amenities_catalog(branch)}

    def create_booking(self, request: Any) -> Dict[str, Any]:
        if hasattr(request, "model_dump"):
            booking_dict = request.model_dump()
        elif isinstance(request, dict):
            booking_dict = dict(request)
        else:
            booking_dict = dict(request)

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
            price_per_night = float(
                r_data.get("pricePerNight")
                or r_data.get("price_per_night")
                or r_data.get("daily_rate")
                or 0.0
            )
            r_data["nights"] = nights
            r_data["pricePerNight"] = price_per_night
            r_data["totalPrice"] = price_per_night * nights
            r_data["type"] = r_data.get("room_type_id") or "Room"
            r_data["maxCapacity"] = r_data.get("capacity") or r_data.get("maxCapacity") or 2

            if "id" not in r_data and "room_number" in r_data:
                r_data["id"] = f"room-{r_data['room_number']}"
            if "name" not in r_data:
                rtype = r_data.get("room_type_id", "")
                r_data["name"] = f"Room {r_data.get('room_number', '')} ({rtype})"
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
                    booking_status=b.get("booking_status", "Confirmed"),
                    start_date=str(b.get("start_date") or b.get("checkIn", "")[:10]),
                    end_date=str(b.get("end_date") or b.get("checkOut", "")[:10]),
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
            booking_status=b.get("booking_status", "Confirmed"),
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
        if current_status != "Confirmed":
            raise HTTPException(
                status_code=400,
                detail=f"Booking is not in 'Confirmed' status (current status: {current_status}).",
            )

        in_time = check_in_time or datetime.now().strftime("%H:%M:%S")
        self.booking_repo.update_booking(
            booking_id,
            {"booking_status": "Checked-In", "checked_in_time": in_time},
        )
        return CheckInResponse(
            booking_id=booking_id,
            booking_status="Checked-In",
            checked_in_time=in_time,
        )

    def check_out(
        self, booking_id: int, check_out_time: Optional[str] = None
    ) -> CheckOutResponse:
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status != "Checked-In":
            raise HTTPException(
                status_code=400,
                detail=f"Booking is not in 'Checked-In' status (current status: {current_status}).",
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
            {"booking_status": "Checked-Out", "checked_out_time": out_time},
        )
        return CheckOutResponse(
            booking_id=booking_id,
            booking_status="Checked-Out",
            checked_out_time=out_time,
        )

    def cancel_booking(self, booking_id: int) -> CancelBookingResponse:
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status in ("Checked-In", "Checked-Out"):
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel a booking that is already Checked-In or Checked-Out.",
            )

        self.booking_repo.update_booking(booking_id, {"booking_status": "Cancelled"})
        return CancelBookingResponse(
            booking_id=booking_id,
            booking_status="Cancelled",
        )
