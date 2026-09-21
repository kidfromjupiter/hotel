from datetime import date

from app.repositories.rooms_repo import RoomsRepo


class RoomService:
    def __init__(self, repo: RoomsRepo) -> None:
        self.repo = repo

    def get_rooms(
        self, check_in: date, check_out: date, branch: str, children: int, adults: int
    ):

        return self.repo.get_rooms(check_in, check_out, branch, children, adults)
