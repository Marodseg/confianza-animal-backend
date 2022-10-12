from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.size import Size


class Animal(BaseModel):
    name: str
    age: Optional[int]
    gender: Gender
    photos: List[str]
    weight: float
    size: Size
    neutered: bool
    description: str
    healthy: bool
    wormed: bool
    vaccinated: bool
    birth_date: Optional[datetime.date]
    activity_level: Activity
    microchip: bool
    is_urgent: bool

    class Config:
        schema_extra = {
            "example": {
                "name": "Prueba",
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
            }
        }


class Dog(Animal):
    raze: DogRaze

    class Config:
        schema_extra = {
            "example": {
                "name": "Prueba",
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
                "raze": DogRaze.akita,
            }
        }


class Cat(Animal):
    raze: CatRaze

    class Config:
        schema_extra = {
            "example": {
                "name": "Prueba",
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
        }
