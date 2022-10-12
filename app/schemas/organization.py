import datetime
import re

from pydantic import BaseModel, validator
from typing import Optional, List

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
    active: bool = True
    deleted_at: Optional[datetime.datetime]
    photo: Optional[str]
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]
    zone: Province

    @validator("phone")
    def phone_must_be_valid(cls, v) -> str:
        if not re.match(r"^[0-9]{9}$", v):
            raise ValueError("Phone number must have 9 digits")
        return v

    @validator("email")
    def email_must_be_valid(cls, v) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Email is not valid")
        return v

    @validator("password")
    def password_must_be_valid(cls, v) -> str:
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$", v):
            raise ValueError(
                "Password must have at least 4 characters, 1 number and 1 letter"
            )
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Prueba",
                "email": "prueba@prueba.com",
                "password": "123456",
                "phone": "123456789",
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
                        "birth_date": datetime.datetime(2021, 5, 1),
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
                        "birth_date": datetime.datetime(2021, 5, 1),
                        "activity_level": Activity.low,
                        "microchip": True,
                        "is_urgent": True,
                        "raze": CatRaze.persa,
                    }
                ],
                "zone": Province.alava,
            }
        }


class OrganizationCreate(BaseModel):
    name: str
    email: str
    phone: str
    zone: Province
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]

    class Config:
        orm_mode = True
