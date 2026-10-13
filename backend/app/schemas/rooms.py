from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    room_number: int = Field(ge=1, le=32767)
    branch_id: int = Field(gt=0)
    room_type_id: str = Field(min_length=1, max_length=50)
    capacity: int = Field(ge=1, le=32767)
