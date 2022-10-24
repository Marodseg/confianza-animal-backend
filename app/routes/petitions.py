import datetime
from typing import List

from app.config.database import db
from fastapi import APIRouter, HTTPException, Depends

from app.routes.auth import firebase_authentication
from app.schemas.petition import Petition
from app.utils import exists_dog_in_animals, exists_cat_in_animals

router = APIRouter()


# Create a petition for a dog
@router.post("/{dog_id}", status_code=200, response_model=Petition)
async def ask_for_dog(dog_id: str, email: str = Depends(firebase_authentication)):
    user = db.collection("users").where("email", "==", email).get()[0].to_dict()
    try:
        if exists_dog_in_animals(dog_id):
            petition = Petition(
                user_id=user["id"], dog_id=dog_id, date=datetime.datetime.now()
            )
            db.collection("petitions").document(user["id"]).set(petition.dict())
            return petition
    except HTTPException:
        raise HTTPException(status_code=400, detail="Error creating petition")


# Create a petition for a cat
@router.post("/{cat_id}", status_code=200, response_model=Petition)
async def ask_for_cat(cat_id: str, email: str = Depends(firebase_authentication)):
    user = db.collection("users").where("email", "==", email).get()[0].to_dict()
    try:
        if exists_cat_in_animals(cat_id):
            petition = Petition(
                user_id=user["id"], cat_id=cat_id, date=datetime.datetime.now()
            )
            db.collection("petitions").document(user["id"]).set(petition.dict())
            return petition
    except HTTPException:
        raise HTTPException(status_code=400, detail="Error creating petition")


# Get petition by user id
@router.get("/{user_id}", status_code=200, response_model=List[Petition])
async def get_petition_by_user_id(user_id: str):
    petitions = db.collection("petitions").where("user_id", "==", user_id).get()
    if not petitions:
        raise HTTPException(status_code=404, detail="Petition not found")

    return [Petition(**petition.to_dict()) for petition in petitions]
