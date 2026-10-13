from typing import Any, Dict, List
from fastapi.encoders import jsonable_encoder

from app.repositories.services_repo import ServicesRepo


class ServicesService:
    def __init__(self, repo: ServicesRepo) -> None:
        self.repo = repo

    def list_services(self) -> List[Dict[str, Any]]:
        return jsonable_encoder([
            {**row, "description": row.get("description") or row["service_name"]}
            for row in self.repo.get_services()
        ])

    def charge_service(
        self, booking_id: int, service_id: int, service_dates: int = 1
    ) -> Dict[str, Any]:
        return self.repo.charge_service(
            booking_id=booking_id,
            service_id=service_id,
            service_dates=service_dates,
        )
