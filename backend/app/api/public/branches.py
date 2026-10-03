from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from app.api.dependencies import get_branch_service
from app.services.branch_service import BranchService

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
def list_branches(
    branch_service: BranchService = Depends(get_branch_service),
):
    """Public customer endpoint to list available hotel branches from database."""
    return branch_service.list_branches()
