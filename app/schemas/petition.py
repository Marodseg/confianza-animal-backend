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
    status: PetitionStatus = PetitionStatus.initiated
    user_message: str
    organization_message: Optional[str]
    organization_name: Optional[str]
    visible: bool = True
    info_updated: bool = False
    docu_updated: bool = False
    home_type: str
    home_type_bool: bool = False
    free_time: str
    free_time_bool: bool = False
    previous_experience: str
    previous_experience_bool: bool = False
    frequency_travel: str
    frequency_travel_bool: bool = False
    kids: str
    kids_bool: bool = False
    other_animals: str
    other_animals_bool: bool = False

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
                "status": PetitionStatus.initiated,
                "message": "Prueba",
                "organization_name": "Prueba",
                "visible": True,
            }
        }
