from datetime import datetime

from fastapi import Request

from app.repositories.booking_flow_repo import BookingFlowRepository


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
