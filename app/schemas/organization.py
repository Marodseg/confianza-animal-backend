from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.animal import Dog, Cat
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size


class Organization(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    active: bool
    deleted_at: Optional[datetime.date]
    photo: Optional[str]
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]
    zone: Province

    class Config:
        schema_extra = {
            "example": {
                "name": "Prueba",
                "email": "prueba@prueba.com",
                "password": "123456",
                "phone": "123456789",
                "active": True,
                "dogs": [
                    {
                        "name": "Perro1",
                        "age": 1,
                        "gender": Gender.male,
                        "photos": [
                            "https://www.image.com/image.jpg",
                            "https://www.image.com/image2.jpg",
                        ],
                        "weight": 1.0,
                        "size": Size.small,
                        "neutered": True,
                        "description": "Prueba",
                        "healthy": True,
                        "wormed": True,
                        "vaccinated": True,
                        "birth_date": "2021-05-01",
                        "activity_level": Activity.low,
                        "microchip": True,
                        "is_urgent": True,
                        "raze": DogRaze.pitbull,
                    },
                ],
                "cats": [
                    {
                        "name": "Gato1",
                        "age": 1,
                        "gender": Gender.male,
                        "photos": [
                            "https://www.image.com/image.jpg",
                            "https://www.image.com/image2.jpg",
                        ],
                        "weight": 1.0,
                        "size": Size.small,
                        "neutered": True,
                        "description": "Prueba",
                        "healthy": True,
                        "wormed": True,
                        "vaccinated": True,
                        "birth_date": "2021-05-01",
                        "activity_level": Activity.low,
                        "microchip": True,
                        "is_urgent": True,
                        "raze": CatRaze.persa,
                    }
                ],
                "deleted_at": "2021-05-01",
                "photo": "https://www.image.com/image.jpg",
                "zone": Province.alava,
            }
        }
