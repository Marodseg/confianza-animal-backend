import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.enums.petition_status import PetitionStatus


class Petition(BaseModel):
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
                "user_id": "123456789",
                "dog_id": "123456789",
                "cat_id": "123456789",
                "date": datetime.datetime.now(),
                "status": PetitionStatus.pending,
                "message": "Prueba",
            }
        }
