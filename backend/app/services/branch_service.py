from typing import Any, Dict, List

from app.repositories.branches_repo import BranchesRepo


class BranchService:
    def __init__(self, repo: BranchesRepo) -> None:
        self.repo = repo

    def list_branches(self) -> List[Dict[str, Any]]:
        return self.repo.get_branches()
