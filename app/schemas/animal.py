import datetime

from pydantic import BaseModel, validator
from typing import Optional, List

from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size


class Animal(BaseModel):
    # The id will be set automatically by the database (setting it here will generate always the same id)
    id: str = None
    name: str
    years: Optional[int]
    months: Optional[int]
    gender: Gender
    photos: Optional[List[str]] = []
    weight: float
    size: Size
    zone: Province
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

    @validator("months")
    def months_must_be_valid(cls, v) -> str:
        if v is not None:
            if v < 0 or v > 11:
                raise ValueError("Months must be between 0 and 11")
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Prueba",
                "years": 1,
                "months": 1,
                "gender": Gender.male,
                "photos": [
                    "https://www.image.com/image.jpg",
                    "https://www.image.com/image2.jpg",
                ],
                "weight": 1.0,
                "size": Size.small,
                "zone": Province.alava,
                "neutered": True,
                "description": "Prueba",
                "healthy": True,
                "wormed": True,
                "vaccinated": True,
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
                "organization_name": "Prueba",
                "organization_phone": "+34111111111",
                "organization_photo": "Prueba",
            }
        }


class Dog(Animal):
    raze: DogRaze

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Prueba",
                "years": 1,
                "months": 1,
                "gender": Gender.male,
                "photos": [
                    "https://www.image.com/image.jpg",
                    "https://www.image.com/image2.jpg",
                ],
                "weight": 1.0,
                "size": Size.small,
                "zone": Province.alava,
                "neutered": True,
                "description": "Prueba",
                "healthy": True,
                "wormed": True,
                "vaccinated": True,
                "activity_level": Activity.low,
                "microchip": True,
                "is_urgent": True,
                "organization_name": "Prueba",
                "organization_phone": "+34111111111",
                "organization_photo": "Prueba",
                "raze": DogRaze.akita,
            }
        }


class DogUpdate(Animal):
    name: Optional[str]
    years: Optional[int]
    months: Optional[int]
    gender: Optional[Gender]
    photos: Optional[List[str]]
    weight: Optional[float]
    size: Optional[Size]
    zone: Optional[Province]
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

    @validator("months")
    def months_must_be_valid(cls, v) -> str:
        if v < 0 or v > 11:
            raise ValueError("Months must be between 0 and 11")
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Prueba",
                "years": 1,
                "months": 1,
                "gender": Gender.male,
                "photos": [
                    "https://www.image.com/image.jpg",
                    "https://www.image.com/image2.jpg",
                ],
                "weight": 1.0,
                "size": Size.small,
                "zone": Province.alava,
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
                "years": 1,
                "months": 1,
                "gender": Gender.male,
                "photos": [
                    "https://www.image.com/image.jpg",
                    "https://www.image.com/image2.jpg",
                ],
                "weight": 1.0,
                "size": Size.small,
                "zone": Province.alava,
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
    years: Optional[int]
    months: Optional[int]
    gender: Optional[Gender]
    photos: Optional[List[str]]
    weight: Optional[float]
    size: Optional[Size]
    zone: Optional[Province]
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

    @validator("months")
    def months_must_be_valid(cls, v) -> str:
        if v < 0 or v > 11:
            raise ValueError("Months must be between 0 and 11")
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Prueba",
                "years": 1,
                "months": 1,
                "gender": Gender.male,
                "photos": [
                    "https://www.image.com/image.jpg",
                    "https://www.image.com/image2.jpg",
                ],
                "weight": 1.0,
                "size": Size.small,
                "zone": Province.alava,
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
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "dogs": [
                    {
                        "name": "Prueba",
                        "years": 1,
                        "months": 1,
                        "gender": Gender.male,
                        "photos": [
                            "https://www.image.com/image.jpg",
                            "https://www.image.com/image2.jpg",
                        ],
                        "weight": 1.0,
                        "size": Size.small,
                        "zone": Province.alava,
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
                        "years": 1,
                        "months": 1,
                        "gender": Gender.male,
                        "photos": [
                            "https://www.image.com/image.jpg",
                            "https://www.image.com/image2.jpg",
                        ],
                        "weight": 1.0,
                        "size": Size.small,
                        "zone": Province.alava,
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
