import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.enums.petition_status import PetitionStatus


class Petition(BaseModel):
    id: str = None
    user_id: str
    dog_id: Optional[str]
    cat_id: Optional[str]
    date: datetime.datetime
    status: PetitionStatus = PetitionStatus.pending
    message: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_id": "1",
                "dog_id": "1",
                "cat_id": "1",
                "date": datetime.datetime.now(),
                "status": PetitionStatus.pending,
                "message": "Prueba",
            }
        }
