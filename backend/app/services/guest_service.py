from typing import Any, Dict, List, Optional

from app.repositories.guests_repo import GuestsRepo


class GuestService:
    def __init__(self, repo: GuestsRepo) -> None:
        self.repo = repo

    def list_guests(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.repo.get_all_guests(search=search)

    def get_guest(self, guest_id: int) -> Optional[Dict[str, Any]]:
        return self.repo.get_guest_by_id(guest_id)

    def lookup_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_guest_by_phone(phone)

    def update_phone(self, guest_id: int, phone: str) -> Dict[str, Any]:
        return self.repo.update_guest_phone(guest_id, phone)

    def enroll_membership(self, guest_id: int, membership_id: int = 1) -> Dict[str, Any]:
        return self.repo.enroll_guest_membership(guest_id, membership_id)

    def enroll_by_phone(self, name: str, phone: str, email: str) -> Dict[str, Any]:
        return self.repo.enroll_by_phone(name, phone)
