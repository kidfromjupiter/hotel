# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends

from app.api.dependencies import get_branch_service
from app.services.branch_service import BranchService

router = APIRouter()


@router.get("/")
def list_branches(service: BranchService = Depends(get_branch_service)):
    return service.get_all_branches()
