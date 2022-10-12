import datetime
from uuid import uuid4

from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: str
    email: str
    name: str
    deleted_at: Optional[datetime.datetime]
    password: str
    photo: Optional[str]
    active: bool

    class Config:
        schema_extra = {
            "example": {
                "id": str(uuid4()),
                "email": "prueba@prueba.com",
                "name": "Prueba",
                "deleted_at": datetime.datetime(2021, 5, 1),
                "password": "123456",
                "photo": "https://www.image.com/image.jpg",
                "active": True,
            }
        }
