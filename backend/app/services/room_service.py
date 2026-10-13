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

    def get_room_types(self):
        from fastapi import HTTPException

        if self.repo.db is None:
            raise HTTPException(503, "Database unavailable")
        return [dict(row) for row in self.repo.get_room_types()]

    def create_room(self, payload):
        from fastapi import HTTPException
        from psycopg2.errors import ForeignKeyViolation, UniqueViolation

        if self.repo.db is None:
            raise HTTPException(503, "Database unavailable")
        try:
            return dict(self.repo.create_room(**payload.model_dump()))
        except UniqueViolation:
            raise HTTPException(
                409, "Room number already exists in this branch"
            )
        except ForeignKeyViolation:
            raise HTTPException(422, "Invalid branch or room type")
