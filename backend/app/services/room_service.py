from datetime import date

from app.repositories.rooms_repo import RoomsRepo


class RoomService:
    def __init__(self, repo: RoomsRepo) -> None:
        self.repo = repo

    def get_rooms(
        self, check_in: date, check_out: date, branch: str, children: int, adults: int
    ):

        branch_lower = branch.lower() if branch else None
        return self.repo.get_rooms(
            check_in, check_out, branch_lower, children, adults
        )

    def get_all_rooms(self):
        return self.repo.get_all_rooms()
