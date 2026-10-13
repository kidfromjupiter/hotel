from typing import Any, Dict, List, Optional
from fastapi.encoders import jsonable_encoder

from app.repositories.guests_repo import GuestsRepo


class GuestService:
    def __init__(self, repo: GuestsRepo) -> None:
        self.repo = repo

    def list_guests(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        return jsonable_encoder(self.repo.get_all_guests(search=search))

    def get_guest(self, guest_id: int) -> Optional[Dict[str, Any]]:
        row = self.repo.get_guest_by_id(guest_id)
        return jsonable_encoder(row) if row else None

    def lookup_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        row = self.repo.get_guest_by_phone(phone)
        return jsonable_encoder(row) if row else None

    def get_payment_history(
        self, query: str, branch_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        rows = self.repo.get_payment_history_rows(query=query, branch_id=branch_id)
        if rows is None:
            return None
        guest, summary, bookings = rows
        for booking in bookings:
            booking["branch_name"] = (booking.get("branch_name") or "Unknown").title()
        return jsonable_encoder({"guest": guest, "summary": summary, "bookings": bookings})

    def create_guest(self, phone: str, name: str = "Guest") -> Optional[Dict[str, Any]]:
        return self.repo.create_guest(phone, name)

    def update_phone(self, guest_id: int, phone: str) -> Dict[str, Any]:
        digits = "".join(c for c in phone if c.isdigit())
        if digits.startswith("94"):
            digits = digits[2:]
        elif digits.startswith("0"):
            digits = digits[1:]
        if not digits or int(digits) > 2147483647:
            return {"success": False, "message": "Invalid phone number format"}
        row = self.repo.update_guest_phone(guest_id, int(digits))
        if row is None:
            return {"success": False, "message": "Guest not found"}
        return {"success": True, "message": "Phone number updated successfully",
                "guest_id": row["guest_id"], "phone_number": str(row["phone_number"])}

    def enroll_membership(self, guest_id: int, membership_id: int = 1) -> Dict[str, Any]:
        row = self.repo.enroll_guest_membership(guest_id, membership_id)
        if row is None:
            return {"success": False, "message": "Guest not found"}
        return {"success": True, "message": "Guest enrolled in membership successfully",
                "guest_id": row["guest_id"], "membership_id": row["membership_id"]}
