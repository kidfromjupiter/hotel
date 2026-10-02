from app.repositories.guests_repo import GuestsRepo


class GuestService:
    def __init__(self, repo: GuestsRepo) -> None:
        self.repo = repo

    def get_all_guests(self):
        return self.repo.get_all_guests()
