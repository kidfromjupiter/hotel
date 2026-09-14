from fastapi import APIRouter

router = APIRouter()


@router.get("/occupancy")
def get_occupancy_report():
    return {"report": "occupancy", "data": []}
