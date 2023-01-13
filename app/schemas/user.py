import re

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
    favorites: dict = {"dogs": Optional[List[Dog]], "cats": Optional[List[Cat]]}

    @validator("email")
    def email_must_be_valid(cls, v) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Email is not valid")
        return v

    @validator("password")
    def password_must_be_valid(cls, v) -> str:
        # The password must be at least 8 characters long and contain at least one number, one uppercase and one symbol
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", v
        ):
            raise ValueError(
                "Password must have 8 characters and contain at least one number, one uppercase and one symbol"
            )
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
    active: Optional[bool]
    favorites: dict = {"dogs": Optional[List[Dog]], "cats": Optional[List[Cat]]}

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
