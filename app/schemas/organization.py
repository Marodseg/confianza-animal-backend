import datetime
import re

from pydantic import BaseModel, validator
from typing import Optional, List

from app.schemas.animal import Dog, Cat
from app.schemas.enums.provinces import Province


class Organization(BaseModel):
    name: str
    email: str
    password: str = None
    phone: str
    active: bool = True
    deleted_at: Optional[datetime.datetime]
    photo: Optional[str]
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]
    zone: Province

    @validator("phone")
    def phone_must_be_valid(cls, v) -> str:
        # phone number with prefix and 9 digits
        if not re.match(r"^\+34\d{9}$", v):
            raise ValueError("Invalid phone number. Must be +34XXXXXXXXX")
        return v

    @validator("email")
    def email_must_be_valid(cls, v) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Email is not valid")
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Prueba",
                "email": "prueba@prueba.com",
                "password": "aAbBcCdD1",
                "phone": "+34123456789",
                "zone": Province.alava,
            }
        }


class OrganizationCreate(BaseModel):
    name: str
    email: str
    phone: str
    zone: Province

    class Config:
        orm_mode = True
