from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class AmenitiesRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_amenities_for_branch(self, branch: str) -> List[Dict[str, Any]]:
        branch_lower = branch.lower() if branch else "colombo"

        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT get_branch_amenities(%s)", (branch_lower,))
                    row = cursor.fetchone()
                    if row and "get_branch_amenities" in row and row["get_branch_amenities"]:
                        return row["get_branch_amenities"]
            except Exception:
                pass

        # Fallback catalog based on branch
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
