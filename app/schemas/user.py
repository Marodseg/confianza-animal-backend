import datetime
import re
from uuid import uuid4

from pydantic import BaseModel, validator
from typing import Optional, List

from app.schemas.animal import Dog, Cat


class User(BaseModel):
    id: str = None
    email: str = None
    name: str
    password: str = None
    photo: Optional[str]
    active: bool = True
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]

    @validator("email")
    def email_must_be_valid(cls, v) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Email is not valid")
        return v

    @validator("password")
    def password_must_be_valid(cls, v) -> str:
        if len(v) < 6:
            raise ValueError("Password must have 6 characters at least")
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "user@prueba.com",
                "name": "Prueba",
                "password": "",
            }
        }


class UserCreate(BaseModel):
    id: str
    email: str
    name: str

    class Config:
        orm_mode = True


class UserView(BaseModel):
    id: str
    email: str
    name: str
    photo: Optional[str]

    class Config:
        orm_mode = True


class UserUpdateIn(BaseModel):
    name: str
    photo: Optional[str]

    class Config:
        orm_mode = True


class UserUpdateOut(BaseModel):
    id: str = None
    email: str = None
    name: str
    photo: Optional[str]
    dogs: Optional[List[Dog]]
    cats: Optional[List[Cat]]

    class Config:
        orm_mode = True
