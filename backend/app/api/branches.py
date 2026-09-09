from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_branches():
    return [{"branch_id": 1, "branch_name": "Colombo"}, {"branch_id": 2, "branch_name": "Kandy"}, {"branch_id": 3, "branch_name": "Galle"}]
