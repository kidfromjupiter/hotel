import random
import string
from datetime import datetime
from typing import Any, Dict, List, Optional


class BookingFlowRepository:
    def __init__(self):
        self._bookings: List[Dict[str, Any]] = []
        self._next_id: int = 500001

    def clear(self):
        self._bookings.clear()

    def generate_booking_ref(self) -> str:
        random_code = "".join(random.choices(string.digits, k=4))
        return f"SKN-{random_code}"

    def save_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(booking_data)
        if "booking_id" not in record:
            record["booking_id"] = self._next_id
            self._next_id += 1
        if "bookingRef" not in record or not record["bookingRef"]:
            record["bookingRef"] = self.generate_booking_ref()
        if "booking_status" not in record:
            record["booking_status"] = "Confirmed"
        self._bookings.append(record)
        return record

    def find_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        for b in self._bookings:
            if b.get("booking_id") == booking_id:
                return b
        return None

    def list_all_bookings(self) -> List[Dict[str, Any]]:
        return list(self._bookings)

    def update_booking(self, booking_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        booking = self.find_booking_by_id(booking_id)
        if booking:
            booking.update(updates)
            return booking
        return None

    def is_overlapping(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        # Normalize date strings (YYYY-MM-DD)
        d_start1 = start1[:10]
        d_end1 = end1[:10]
        d_start2 = start2[:10]
        d_end2 = end2[:10]
        return max(d_start1, d_start2) < min(d_end1, d_end2)

    def is_room_booked(self, room_id: str, start_date: str, end_date: str) -> bool:
        for b in self._bookings:
            b_room = b.get("roomId")
            if b_room == room_id:
                b_start = b.get("start_date") or b.get("checkIn") or ""
                b_end = b.get("end_date") or b.get("checkOut") or ""
                if b_start and b_end and self.is_overlapping(b_start, b_end, start_date, end_date):
                    return True
        return False

    def get_rooms_catalog(self, branch: str) -> List[Dict[str, Any]]:
        branch_lower = branch.lower()
        if branch_lower == "kandy":
            return [
                {
                    "id": "standard-room",
                    "type": "Standard Mountain View",
                    "name": "Standard Mountain View",
                    "description": "Charming room with scenic hillside views of the Knuckles mountain range.",
                    "pricePerNight": 25000,
                    "membershipPrice": 22500,
                    "membershipDiscount": 10,
                    "maxCapacity": 2,
                    "features": ["Queen Bed", "Mountain View", "Tea Station", "Free Wi-Fi"],
                    "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
                {
                    "id": "deluxe-room",
                    "type": "Deluxe Plantation Suite",
                    "name": "Deluxe Plantation Suite",
                    "description": "Luxurious suite nestled among tea gardens with a private terrace and colonial charm.",
                    "pricePerNight": 42000,
                    "membershipPrice": 37800,
                    "membershipDiscount": 10,
                    "maxCapacity": 3,
                    "features": ["King Bed", "Private Terrace", "Fireplace", "En-suite Bath"],
                    "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": True,
                },
                {
                    "id": "family-suite",
                    "type": "Royal Hills Family Suite",
                    "name": "Royal Hills Family Suite",
                    "description": "Spacious two-bedroom retreat ideal for families visiting historic Kandy.",
                    "pricePerNight": 58000,
                    "membershipPrice": 52200,
                    "membershipDiscount": 10,
                    "maxCapacity": 4,
                    "features": ["2 King Beds", "Balcony", "Separate Living Area", "Breakfast Included"],
                    "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
            ]
        elif branch_lower == "galle":
            return [
                {
                    "id": "standard-room",
                    "type": "Standard Coastal Haven",
                    "name": "Standard Coastal Haven",
                    "description": "Bright and airy coastal room steps away from the historic ramparts of Galle Fort.",
                    "pricePerNight": 28000,
                    "membershipPrice": 25200,
                    "membershipDiscount": 10,
                    "maxCapacity": 2,
                    "features": ["Queen Bed", "Sea Breeze Balcony", "Mini Bar", "Free Wi-Fi"],
                    "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
                {
                    "id": "deluxe-room",
                    "type": "Oceanview Deluxe Suite",
                    "name": "Oceanview Deluxe Suite",
                    "description": "Uninterrupted panoramas of the Indian Ocean with private sunrise patio.",
                    "pricePerNight": 48000,
                    "membershipPrice": 43200,
                    "membershipDiscount": 10,
                    "maxCapacity": 3,
                    "features": ["King Bed", "Ocean View", "Free Minibar", "Rain Shower"],
                    "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": True,
                },
                {
                    "id": "presidential-suite",
                    "type": "Fortress Grand Villa",
                    "name": "Fortress Grand Villa",
                    "description": "Grand heritage villa with private plunge pool and 24/7 dedicated butler service.",
                    "pricePerNight": 75000,
                    "membershipPrice": 67500,
                    "membershipDiscount": 10,
                    "maxCapacity": 4,
                    "features": ["Private Pool", "Butler Service", "Oceanfront", "Gourmet Kitchen"],
                    "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
            ]
        else:
            # Default to Colombo
            return [
                {
                    "id": "standard-room",
                    "type": "City View Standard",
                    "name": "City View Standard",
                    "description": "Sophisticated urban sanctuary overlooking the shimmering Colombo skyline.",
                    "pricePerNight": 25000,
                    "membershipPrice": 22500,
                    "membershipDiscount": 10,
                    "maxCapacity": 2,
                    "features": ["Queen Bed", "City View", "Ergonomic Workspace", "High-Speed Wi-Fi"],
                    "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
                {
                    "id": "deluxe-room",
                    "type": "Executive Oceanfront Deluxe",
                    "name": "Executive Oceanfront Deluxe",
                    "description": "Floor-to-ceiling vistas of Galle Face Green and the vibrant Port City sunsets.",
                    "pricePerNight": 35000,
                    "membershipPrice": 31500,
                    "membershipDiscount": 10,
                    "maxCapacity": 3,
                    "features": ["King Bed", "Ocean View", "Lounge Access", "Marble Bathroom"],
                    "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": True,
                },
                {
                    "id": "presidential-suite",
                    "type": "Skyline Presidential Suite",
                    "name": "Skyline Presidential Suite",
                    "description": "Top-floor sprawling residence offering premier luxury and panoramic ocean views.",
                    "pricePerNight": 65000,
                    "membershipPrice": 58500,
                    "membershipDiscount": 10,
                    "maxCapacity": 4,
                    "features": ["2 King Bedrooms", "Jacuzzi", "Skyline View", "Private Bar"],
                    "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800",
                    "isBestseller": False,
                },
            ]

    def get_amenities_catalog(self, branch: str) -> List[Dict[str, Any]]:
        branch_lower = branch.lower()
        if branch_lower == "kandy":
            return [
                {
                    "id": "kandy-tea-tour",
                    "name": "Ceylon Tea Tasting & Estate Walk",
                    "description": "Guided tasting session and scenic walking tour across organic tea estates.",
                    "price": 4500,
                    "icon": "cup",
                },
                {
                    "id": "spa-ayurveda",
                    "name": "Traditional Ayurvedic Spa Therapy",
                    "description": "60-minute rejuvenating herbal massage and steam bath.",
                    "price": 8500,
                    "icon": "spa",
                },
                {
                    "id": "airport-transfer",
                    "name": "Airport Shuttle Transfer",
                    "description": "Comfortable air-conditioned private vehicle transfer.",
                    "price": 12000,
                    "icon": "car",
                },
            ]
        elif branch_lower == "galle":
            return [
                {
                    "id": "sunset-cruise",
                    "name": "Galle Coastal Sunset Cruise",
                    "description": "Private catamaran boat ride with cocktails along the southern coastline.",
                    "price": 9500,
                    "icon": "water",
                },
                {
                    "id": "surf-lesson",
                    "name": "Private Surfing Lesson",
                    "description": "2-hour beginner or intermediate surf session with certified instructor.",
                    "price": 6000,
                    "icon": "waves",
                },
                {
                    "id": "airport-transfer",
                    "name": "Airport Shuttle Transfer",
                    "description": "Direct highway transfer from BIA Airport to Galle.",
                    "price": 14000,
                    "icon": "car",
                },
            ]
        else:
            return [
                {
                    "id": "airport-pickup",
                    "name": "Airport Pickup & Luxury Transfer",
                    "description": "Luxury chauffeur transfer from Bandaranaike International Airport (BIA).",
                    "price": 5000,
                    "icon": "car",
                },
                {
                    "id": "buffet-breakfast",
                    "name": "Gourmet Oceanview Breakfast Buffet",
                    "description": "Daily lavish breakfast spread featuring international and Sri Lankan delicacies.",
                    "price": 3500,
                    "icon": "restaurant",
                },
                {
                    "id": "spa-access",
                    "name": "SkyNest Spa & Hydrotherapy Day Pass",
                    "description": "Full-day access to sauna, steam rooms, and infinity hydro-pool.",
                    "price": 7500,
                    "icon": "spa",
                },
            ]


booking_flow_repo = BookingFlowRepository()
