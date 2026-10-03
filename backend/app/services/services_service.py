from typing import Any, Dict, List

from app.repositories.services_repo import ServicesRepo


class ServicesService:
    def __init__(self, repo: ServicesRepo) -> None:
        self.repo = repo

    def list_services(self) -> List[Dict[str, Any]]:
        return self.repo.get_services()

    def charge_service(
        self, booking_id: int, service_id: int, service_dates: int = 1
    ) -> Dict[str, Any]:
        return self.repo.charge_service(
            booking_id=booking_id,
            service_id=service_id,
            service_dates=service_dates,
        )

    def add_extra_amenity(
        self, booking_id: int, amenity_id: int, quantity: int = 1
    ) -> Dict[str, Any]:
        return self.repo.add_extra_amenity(
            booking_id=booking_id,
            amenity_id=amenity_id,
            quantity=quantity,
        )
