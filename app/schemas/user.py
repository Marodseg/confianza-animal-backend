from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    email: str
    name: str
    deleted_at: Optional[datetime.date]
    password: str
    photo: Optional[str]
    active: bool

    class Config:
        schema_extra = {
            "example": {
                "email": "prueba@prueba.com",
                "name": "Prueba",
                "deleted_at": "2021-05-01",
                "password": "123456",
                "photo": "https://www.image.com/image.jpg",
                "active": True,
            }
        }
