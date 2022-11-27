import datetime

from pydantic import BaseModel
from typing import Optional, List

from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.size import Size


class Animal(BaseModel):
    # The id will be set automatically by the database (setting it here will generate always the same id)
    id: str = None
    name: str
    age: int
    gender: Gender
    photos: Optional[List[str]] = []
    weight: float
    size: Size
    neutered: bool
    description: str
    healthy: bool
    wormed: bool
    vaccinated: bool
    birth_date: Optional[datetime.datetime]
    activity_level: Activity
    microchip: bool
    is_urgent: bool
    organization_name: str = None
    organization_phone: str = None
    organization_photo: Optional[str]

    class Config:
        orm_mode = True
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
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
            }
        }


class Dog(Animal):
    raze: DogRaze

    class Config:
        orm_mode = True
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
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
                "raze": DogRaze.akita,
            }
        }


class DogUpdate(Animal):
    name: Optional[str]
    age: Optional[int]
    gender: Optional[Gender]
    photos: Optional[List[str]]
    weight: Optional[float]
    size: Optional[Size]
    neutered: Optional[bool]
    description: Optional[str]
    healthy: Optional[bool]
    wormed: Optional[bool]
    vaccinated: Optional[bool]
    birth_date: Optional[datetime.datetime]
    activity_level: Optional[Activity]
    microchip: Optional[bool]
    is_urgent: Optional[bool]
    raze: Optional[DogRaze]

    class Config:
        orm_mode = True
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
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
                "raze": DogRaze.akita,
            }
        }


class Cat(Animal):
    raze: CatRaze

    class Config:
        orm_mode = True
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
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
                "raze": CatRaze.persa,
            }
        }


class CatUpdate(Animal):
    name: Optional[str]
    age: Optional[int]
    gender: Optional[Gender]
    photos: Optional[List[str]]
    weight: Optional[float]
    size: Optional[Size]
    neutered: Optional[bool]
    description: Optional[str]
    healthy: Optional[bool]
    wormed: Optional[bool]
    vaccinated: Optional[bool]
    birth_date: Optional[datetime.datetime]
    activity_level: Optional[Activity]
    microchip: Optional[bool]
    is_urgent: Optional[bool]
    raze: Optional[CatRaze]

    class Config:
        orm_mode = True
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
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
                "raze": CatRaze.persa,
            }
        }


class AnimalsInDB(BaseModel):
    dogs: List[Dog]
    cats: List[Cat]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "dogs": [
                    {
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
                        "activity_level": Activity.low,
                        "microchip": True,
                        "is_urgent": True,
                        "raze": DogRaze.akita,
                    }
                ],
                "cats": [
                    {
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
                        "activity_level": Activity.low,
                        "microchip": True,
                        "is_urgent": True,
                        "raze": CatRaze.persa,
                    }
                ],
            }
        }
