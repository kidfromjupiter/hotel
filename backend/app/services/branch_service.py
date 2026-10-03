from app.repositories.branches_repo import BranchesRepo


class BranchService:
    def __init__(self, repo: BranchesRepo) -> None:
        self.repo = repo

    def get_all_branches(self):
        return self.repo.get_all_branches()
