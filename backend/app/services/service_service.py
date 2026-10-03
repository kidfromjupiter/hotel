from app.repositories.services_repo import ServicesRepo

class ServiceService:
    def __init__(self, repo: ServicesRepo) -> None:
        self.repo = repo

    def get_all_services(self):
        return self.repo.get_all_services()
