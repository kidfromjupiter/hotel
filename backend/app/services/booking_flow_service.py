from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Request

from app.repositories.booking_flow_repo import BookingFlowRepository
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


# TODO: Connect the proper DB to the repo
class BookingFlowService:
    def __init__(self, *, booking_flow_repo: BookingFlowRepository):
        self.booking_flow_repo = booking_flow_repo

    def get_amenities(self, branch: str = "colombo"):
        return {"amenities": self.booking_flow_repo.get_amenities_catalog(branch)}

    def create_booking(self, request: Request):
        booking_dict = request.model_dump()
        saved = self.booking_flow_repo.save_booking(booking_dict)
        return {
            "success": True,
            "bookingRef": saved["bookingRef"],
            "message": "Your reservation has been confirmed successfully!",
        }

    def check_availability(self, request: Request):
        total_guests = request.adults + request.children
        all_rooms = self.booking_flow_repo.get_rooms_catalog(request.branch)

        max_capacity_any_room = max(
            (r.get("maxCapacity", 2) for r in all_rooms), default=2
        )
        if total_guests > max_capacity_any_room:
            return {
                "available": False,
                "rooms": [],
                "message": f"Maximum capacity exceeded. Maximum capacity per room is {max_capacity_any_room} guests.",
            }

        # Calculate nights
        try:
            d_in = datetime.fromisoformat(request.checkIn.replace("Z", "+00:00")).date()
            d_out = datetime.fromisoformat(
                request.checkOut.replace("Z", "+00:00")
            ).date()
            nights = (d_out - d_in).days
        except Exception:
            nights = 1
        if nights < 1:
            nights = 1

        available_rooms = []
        for room in all_rooms:
            if room.get("maxCapacity", 2) < total_guests:
                continue
            if self.booking_flow_repo.is_room_booked(
                room["id"], request.checkIn, request.checkOut
            ):
                continue

            r_data = dict(room)
            r_data["nights"] = nights
            r_data["totalPrice"] = r_data["pricePerNight"] * nights
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
        bookings = self.booking_flow_repo.list_all_bookings()
        results: List[BookingListItem] = []

        for b in bookings:
            if branch_id is not None and b.get("branch_id") != branch_id:
                continue
            if guest_id is not None and b.get("guest_id") != guest_id:
                continue
            if status is not None and b.get("booking_status", "").lower() != status.lower():
                continue
            if start_date is not None and b.get("start_date", "") < start_date:
                continue
            if end_date is not None and b.get("end_date", "") > end_date:
                continue

            results.append(
                BookingListItem(
                    booking_id=b.get("booking_id", 0),
                    guest_name=b.get("guest_name", "Guest"),
                    room_number=b.get("room_number", 101),
                    branch_name=b.get("branch_name", "Colombo"),
                    booking_status=b.get("booking_status", "Confirmed"),
                    start_date=b.get("start_date") or b.get("checkIn", "")[:10],
                    end_date=b.get("end_date") or b.get("checkOut", "")[:10],
                )
            )
        return results

    def get_booking_by_id(self, booking_id: int) -> BookingDetailResponse:
        b = self.booking_flow_repo.find_booking_by_id(booking_id)
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
            start_date=b.get("start_date") or b.get("checkIn", "")[:10],
            end_date=b.get("end_date") or b.get("checkOut", "")[:10],
            checked_in_time=b.get("checked_in_time"),
            checked_out_time=b.get("checked_out_time"),
            adult_count=b.get("adult_count", 2),
            children_count=b.get("children_count", 0),
            service_charges=services,
            invoice_status=b.get("invoice_status", "PENDING"),
            grand_total=float(b.get("grand_total", 0.0)),
            amount_paid=float(b.get("amount_paid", 0.0)),
        )

    def check_in(self, booking_id: int, check_in_time: Optional[str] = None) -> CheckInResponse:
        b = self.booking_flow_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status != "Confirmed":
            raise HTTPException(
                status_code=400,
                detail=f"Booking is not in 'Confirmed' status (current status: {current_status}).",
            )

        in_time = check_in_time or datetime.now().strftime("%H:%M:%S")
        self.booking_flow_repo.update_booking(
            booking_id,
            {"booking_status": "Checked-In", "checked_in_time": in_time},
        )
        return CheckInResponse(
            booking_id=booking_id,
            booking_status="Checked-In",
            checked_in_time=in_time,
        )

    def check_out(self, booking_id: int, check_out_time: Optional[str] = None) -> CheckOutResponse:
        b = self.booking_flow_repo.find_booking_by_id(booking_id)
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
        self.booking_flow_repo.update_booking(
            booking_id,
            {"booking_status": "Checked-Out", "checked_out_time": out_time},
        )
        return CheckOutResponse(
            booking_id=booking_id,
            booking_status="Checked-Out",
            checked_out_time=out_time,
        )

    def cancel_booking(self, booking_id: int) -> CancelBookingResponse:
        b = self.booking_flow_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")

        current_status = b.get("booking_status", "")
        if current_status in ("Checked-In", "Checked-Out"):
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel a booking that is already Checked-In or Checked-Out.",
            )

        self.booking_flow_repo.update_booking(booking_id, {"booking_status": "Cancelled"})
        return CancelBookingResponse(
            booking_id=booking_id,
            booking_status="Cancelled",
        )
