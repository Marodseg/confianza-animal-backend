from typing import List

from app.config.database import db, realtime_db
from fastapi import APIRouter

from app.schemas.animal import Animal

router = APIRouter()


# post animal to cloud database
@router.post("/animal", status_code=201)
async def post_animal(animal: Animal):
    db.collection("animals").document().set(animal.dict())
    return {"message": "Animal created successfully"}
