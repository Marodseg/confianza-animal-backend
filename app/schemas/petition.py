import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.animal import Cat, Dog
from app.schemas.enums.petition_status import PetitionStatus


class Petition(BaseModel):
    id: str = None
    user_id: str
    dog: Optional[Dog]
    cat: Optional[Cat]
    date: datetime.datetime
    status: PetitionStatus = PetitionStatus.pending
    message: Optional[str]
    organization_name: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_id": "1",
                "dog": "{}",
                "cat": "{}",
                "date": datetime.datetime.now(),
                "status": PetitionStatus.pending,
                "message": "Prueba",
                "organization_name": "Prueba",
            }
        }
