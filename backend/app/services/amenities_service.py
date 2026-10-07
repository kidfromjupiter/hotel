from typing import Any, Dict

from app.repositories.amenities_repo import AmenitiesRepo


class AmenitiesService:
    def __init__(self, repo: AmenitiesRepo) -> None:
        self.repo = repo

    def get_amenities(self, branch: str = "colombo") -> Dict[str, Any]:
        amenities = self.repo.get_amenities_for_branch(branch)
        return {"amenities": amenities}
