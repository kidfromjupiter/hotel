from datetime import date
from fastapi.encoders import jsonable_encoder

from app.repositories.rooms_repo import RoomsRepo


class RoomService:
    def __init__(self, repo: RoomsRepo) -> None:
        self.repo = repo

    def get_rooms(
        self, check_in: date, check_out: date, branch: str, children: int, adults: int
    ):

        rows = self.repo.get_rooms(check_in, check_out, branch.lower() if branch else None, children, adults)
        return jsonable_encoder([
            {**row, "branch_name": row["branch_name"].title(),
             "price_per_night": row["daily_rate"]}
            for row in rows
        ])

    def get_all_rooms(self):
        return self.repo.get_all_rooms()
