import datetime
from typing import List, Optional

from starlette.responses import JSONResponse

from app.config.database import db
from fastapi import APIRouter, HTTPException, Depends

from app.routes.auth import firebase_email_authentication, firebase_uid_authentication
from app.schemas.animal import AnimalsInDB
from app.schemas.petition import Petition
from app.utils import exists_dog_in_animals, exists_cat_in_animals, generate_uuid

router = APIRouter()


# Create a petition for a dog
@router.post("/dog/{dog_id}", status_code=200, response_model=Petition)
async def ask_for_dog(
    dog_id: str,
    message: Optional[str],
    email: str = Depends(firebase_email_authentication),
):
    user = db.collection("users").where("email", "==", email).get()[0].to_dict()
    animals = AnimalsInDB(
        **db.collection("animals").document("animals").get().to_dict()
    )
    dogs = animals.dogs
    dog = next((dog for dog in dogs if dog.id == dog_id), None)

    if dog:
        petitions = db.collection("petitions").where("user_id", "==", user["id"]).get()

        for petition in petitions:
            petition = Petition(**petition.to_dict())
            if petition.dog:
                if petition.dog.id == dog_id:
                    raise HTTPException(
                        status_code=400,
                        detail="You already have a petition for this dog",
                    )
        try:
            if exists_dog_in_animals(dog_id):
                petition = Petition(
                    id=generate_uuid(),
                    user_id=user["id"],
                    user_name=user["name"],
                    user_email=user["email"],
                    dog=dog,
                    date=datetime.datetime.now(),
                    message=message,
                    organization_name=dog.organization_name,
                )
                db.collection("petitions").document(petition.id).set(
                    petition.dict(), merge=True
                )
                return petition
        except HTTPException:
            raise HTTPException(status_code=400, detail="Error creating petition")
    else:
        raise HTTPException(status_code=404, detail="Dog not found")


# Create a petition for a cat
@router.post("/cat/{cat_id}", status_code=200, response_model=Petition)
async def ask_for_cat(
    cat_id: str,
    message: Optional[str],
    email: str = Depends(firebase_email_authentication),
):
    user = db.collection("users").where("email", "==", email).get()[0].to_dict()
    animals = AnimalsInDB(
        **db.collection("animals").document("animals").get().to_dict()
    )
    cats = animals.cats
    cat = next((cat for cat in cats if cat.id == cat_id), None)

    if cat:
        petitions = db.collection("petitions").where("user_id", "==", user["id"]).get()
        for petition in petitions:
            petition = Petition(**petition.to_dict())
            if petition.cat:
                if petition.cat.id == cat_id:
                    raise HTTPException(
                        status_code=400,
                        detail="You already have a petition for this cat",
                    )
        try:
            if exists_cat_in_animals(cat_id):
                petition = Petition(
                    id=generate_uuid(),
                    user_id=user["id"],
                    user_name=user["name"],
                    user_email=user["email"],
                    cat=cat,
                    date=datetime.datetime.now(),
                    message=message,
                    organization_name=cat.organization_name,
                )
                db.collection("petitions").document(petition.id).set(
                    petition.dict(), merge=True
                )
                return petition
        except HTTPException:
            raise HTTPException(status_code=400, detail="Error creating petition")
    else:
        raise HTTPException(status_code=404, detail="Cat not found")


# Get petition by user logged
@router.get("/user", status_code=200, response_model=List[Petition])
async def get_petition_by_user(email: str = Depends(firebase_email_authentication)):
    user = db.collection("users").where("email", "==", email).get()[0].to_dict()

    petitions = db.collection("petitions").where("user_id", "==", user["id"]).get()
    if not petitions:
        raise HTTPException(status_code=404, detail="Petition not found")

    return [Petition(**petition.to_dict()) for petition in petitions]


# Get petition from organization logged
@router.get("/organization", status_code=200, response_model=List[Petition])
async def get_petition_by_organization(
    uid: str = Depends(firebase_uid_authentication),
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()
    petitions = (
        db.collection("petitions").where("organization_name", "==", org["name"]).get()
    )
    return [Petition(**petition.to_dict()) for petition in petitions]


# Reject a petition by id by user
@router.delete("/{petition_id}/user", status_code=200)
async def reject_petition_by_user(
    petition_id: str, email: str = Depends(firebase_email_authentication)
):
    user = db.collection("users").where("email", "==", email).get()[0].to_dict()
    petitions = db.collection("petitions").where("user_id", "==", user["id"]).get()

    for petition in petitions:
        if petition.id == petition_id:

            if petition.to_dict()["user_id"] != user["id"]:
                raise HTTPException(
                    status_code=404, detail="The user is not the owner of the petition"
                )

            # update the status of the petition
            db.collection("petitions").document(petition_id).update(
                {"status": "rejected"}
            )
            return JSONResponse(
                status_code=200, content={"message": "Petition rejected"}
            )

    raise HTTPException(status_code=404, detail="Petition not found")


# Reject a petition by id by organization
@router.delete("/{petition_id}/organization", status_code=200)
async def reject_petition_by_organization(
    petition_id: str, uid: str = Depends(firebase_uid_authentication)
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    petition = db.collection("petitions").document(petition_id).get().to_dict()

    if petition["organization_name"] != org["name"]:
        raise HTTPException(
            status_code=404,
            detail="The organization is not the owner of the animal",
        )

    db.collection("petitions").document(petition_id).update({"status": "rejected"})
    return JSONResponse(status_code=200, content={"message": "Petition rejected"})


# Accept a petition by id by organization
@router.put("/{petition_id}/organization", status_code=200)
async def accept_petition_by_organization(
    petition_id: str, uid: str = Depends(firebase_uid_authentication)
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    petition = db.collection("petitions").document(petition_id).get().to_dict()

    if petition["organization_name"] != org["name"]:
        raise HTTPException(
            status_code=404,
            detail="The organization is not the owner of the animal",
        )

    db.collection("petitions").document(petition_id).update({"status": "approved"})
    return JSONResponse(status_code=200, content={"message": "Petition accepted"})
