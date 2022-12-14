import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.animal import Cat, Dog
from app.schemas.enums.petition_status import PetitionStatus


class Petition(BaseModel):
    id: str = None
    user_id: str
    user_name: str
    user_email: str
    dog: Optional[Dog]
    cat: Optional[Cat]
    date: datetime.datetime
    status: PetitionStatus = PetitionStatus.pending
    message: str
    organization_name: Optional[str]
    visible: bool = True

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "1",
                "user_id": "1",
                "user_name": "Prueba",
                "user_email": "prueba@prueba.com",
                "dog": "{}",
                "cat": "{}",
                "date": datetime.datetime.now(),
                "status": PetitionStatus.pending,
                "message": "Prueba",
                "organization_name": "Prueba",
            }
        }
