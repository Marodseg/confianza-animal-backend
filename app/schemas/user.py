import datetime
from uuid import uuid4

from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: str = str(uuid4())
    email: str
    name: str
    deleted_at: Optional[datetime.datetime]
    password: str
    photo: Optional[str]
    active: bool = True

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "user@prueba.com",
                "name": "Prueba",
                "password": "123456",
            }
        }


class UserCreate(BaseModel):
    id: str
    email: str
    name: str

    class Config:
        orm_mode = True
