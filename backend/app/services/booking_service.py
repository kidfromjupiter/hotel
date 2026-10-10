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
                    booking_status=b.get("booking_status", "Confirmed"),
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
    def add_service_to_booking(self, booking_id: int, payload):
        b = self.booking_repo.find_booking_by_id(booking_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking does not exist.")
            
        current_status = b.get("booking_status", "")
        if current_status not in ("Confirmed", "Checked-In"):
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
        if b and b.get("booking_status") in ["Confirmed", "Checked-In"]:
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
                    "status": b.get("booking_status", "Confirmed")
                }
            }
        return {"success": False, "message": "Booking not found or not in pending state."}

    def get_pending_booking_by_phone(self, phone: str):
        bookings = self.booking_repo.list_all_bookings()
        for b in bookings:
            # We are using .get() because b is a dictionary
            if b.get("guest_phone") == phone and b.get("booking_status") == "Confirmed":
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
                        "status": b.get("booking_status", "Confirmed")
                    }
                }
        
        # If the loop finishes without finding a match:
        return {"success": False, "message": "Invalid OTP or booking not found."}

    def calculate_bill(self, request: Any) -> Dict[str, Any]:
        """
        Calculates whole bill preview after room selection with desired guest services.
        NOTE: This does NOT update or modify any database record (read-only calculation).
        Allows inspecting whole bill preview so issues can be resolved/committed later.
        """
        if hasattr(request, "model_dump"):
            data = request.model_dump()
        elif isinstance(request, dict):
            data = dict(request)
        else:
            data = dict(request)

        booking_id = data.get("booking_id")
        existing_booking = None
        if booking_id:
            existing_booking = self.booking_repo.get_booking_summary_for_calculation(booking_id)

        # 1. Determine Room Details
        nights = data.get("nights") or 1
        daily_rate = data.get("daily_rate")
        room_type = data.get("room_type") or "Standard Room"
        room_number = data.get("room_number")
        guest_phone = data.get("guest_phone")

        if existing_booking:
            if not daily_rate and existing_booking.get("daily_rate"):
                daily_rate = float(existing_booking["daily_rate"])
            if not room_number:
                room_number = existing_booking.get("room_number")
            if not room_type and existing_booking.get("room_type_id"):
                room_type = existing_booking.get("room_type_id")
            if not guest_phone and existing_booking.get("phone_number"):
                guest_phone = str(existing_booking.get("phone_number"))

        if not daily_rate:
            type_str = str(room_type).upper()
            if "DELUXE" in type_str:
                daily_rate = 22000.0
            elif "FAMILY" in type_str:
                daily_rate = 28000.0
            elif "SUITE" in type_str:
                daily_rate = 35000.0
            else:
                daily_rate = 15000.0

        daily_rate = float(daily_rate)
        nights = max(1, int(nights))

        # 2. Check Membership Discounts
        room_discount_pct = float(data.get("membership_discount_percent") or 0.0)
        service_discount_pct = 0.0

        if guest_phone:
            guest_info = self.booking_repo.get_guest_membership_by_phone(guest_phone)
            if guest_info:
                if guest_info.get("room_discount_percentage") is not None:
                    room_discount_pct = max(room_discount_pct, float(guest_info["room_discount_percentage"]))
                if guest_info.get("service_discount_percentage") is not None:
                    service_discount_pct = float(guest_info["service_discount_percentage"])

        room_subtotal = round(daily_rate * nights, 2)
        room_discount_amount = round(room_subtotal * (room_discount_pct / 100.0), 2)
        room_total = round(room_subtotal - room_discount_amount, 2)

        # 3. Calculate Services
        service_catalog = self.booking_repo.get_service_catalog()
        services_map = {s["service_id"]: s for s in service_catalog}
        services_by_name = {s["service_name"].lower(): s for s in service_catalog}

        requested_services = data.get("services") or []
        services_breakdown = []
        services_subtotal = 0.0
        services_discount_amount = 0.0
        services_total = 0.0

        for item in requested_services:
            if hasattr(item, "model_dump"):
                item_dict = item.model_dump()
            else:
                item_dict = dict(item)

            svc_id = item_dict.get("service_id")
            svc_name = item_dict.get("service_name") or ""
            qty = max(1, int(item_dict.get("quantity", 1)))
            days = max(1, int(item_dict.get("days", 1)))

            matched_svc = services_map.get(svc_id) if svc_id else services_by_name.get(svc_name.lower())
            if matched_svc:
                day_rate = float(matched_svc.get("day_rate", 0.0))
                svc_name = matched_svc.get("service_name", svc_name)
                svc_id = matched_svc.get("service_id", svc_id)
            else:
                day_rate = float(item_dict.get("unit_price") or 0.0)

            item_subtotal = round(day_rate * qty * days, 2)
            item_discount = round(item_subtotal * (service_discount_pct / 100.0), 2)
            item_total = round(item_subtotal - item_discount, 2)

            services_breakdown.append({
                "service_id": svc_id,
                "service_name": svc_name or f"Service {svc_id}",
                "quantity": qty,
                "days": days,
                "day_rate": day_rate,
                "subtotal": item_subtotal,
                "discount_percentage": service_discount_pct,
                "discount_amount": item_discount,
                "total": item_total,
            })

            services_subtotal += item_subtotal
            services_discount_amount += item_discount
            services_total += item_total

        services_subtotal = round(services_subtotal, 2)
        services_discount_amount = round(services_discount_amount, 2)
        services_total = round(services_total, 2)

        # 4. Calculate Taxes
        active_taxes = self.booking_repo.get_active_tax_policies()
        tax_items = []
        taxable_amount = round(room_total + services_total, 2)
        total_tax = 0.0

        for t in active_taxes:
            t_pct = float(t.get("tax_percentage", 0.0))
            t_amt = round(taxable_amount * (t_pct / 100.0), 2)
            total_tax += t_amt
            tax_items.append({
                "tax_name": t.get("tax_name", "Tax"),
                "tax_percentage": t_pct,
                "tax_amount": t_amt,
            })

        total_tax = round(total_tax, 2)
        subtotal = taxable_amount
        grand_total = round(subtotal + total_tax, 2)

        return {
            "booking_id": booking_id,
            "room_charges": {
                "room_type": room_type,
                "room_number": room_number,
                "daily_rate": daily_rate,
                "nights": nights,
                "subtotal": room_subtotal,
                "discount_percentage": room_discount_pct,
                "discount_amount": room_discount_amount,
                "total": room_total,
            },
            "services_charges": {
                "items": services_breakdown,
                "subtotal": services_subtotal,
                "discount_percentage": service_discount_pct,
                "discount_amount": services_discount_amount,
                "total": services_total,
            },
            "taxes": tax_items,
            "subtotal": subtotal,
            "total_tax": total_tax,
            "grand_total": grand_total,
            "is_updated": False,
            "status": "PREVIEW_CALCULATED",
            "note": "Calculated bill preview with selected services. Database records remain un-updated so this can be resolved/finalized later.",
        }

