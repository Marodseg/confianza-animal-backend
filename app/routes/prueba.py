from app.config.database import db, realtime_db
from fastapi import APIRouter

from app.schemas.prueba import User

router = APIRouter()


@router.get("/prueba-cloud", status_code=200)
async def get_data():
    user = db.collection("users").document("prueba").get()

    # To print the values in the console:
    # print('CLOUD DATABASE: ', 'ID_DOC: ', user.id, 'DATA: ', user.to_dict())

    return user.to_dict()


@router.post("/prueba-cloud", status_code=201)
async def post_data(user: User):
    db.collection("users").document().set(user.dict())
    return {"message": "User created successfully"}


@router.get("/prueba-realtime", status_code=200)
async def get_data():
    users = realtime_db.child("users").get()

    # To print the values in the console:
    # print('REALTIME DATABASE: ', users.val())

    return users.val()


@router.post("/prueba-realtime", status_code=201)
async def post_data(user: User):
    realtime_db.child("users").push(user.dict())
    return {"message": "User created successfully"}
