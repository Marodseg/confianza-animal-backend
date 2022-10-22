import uuid

from google.cloud.firestore_v1 import DELETE_FIELD
from starlette.responses import JSONResponse

from app.config.database import db, firebase_admin_auth, pyrebase_auth
from fastapi import APIRouter, HTTPException, Depends

from app.routes.auth import firebase_authentication
from app.schemas.user import User, UserCreate, UserView, UserUpdateIn, UserUpdateOut
from app.utils import (
    exists_email_in_user,
    exists_id_in_user,
    generate_uuid,
)

router = APIRouter()


# Get user by id
@router.get("/{user_id}", status_code=200, response_model=UserView)
async def get_user_by_id(user_id: str):
    user = db.collection("users").document(user_id).get().to_dict()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Get animals by user id
@router.get("/animals/{user_id}", status_code=200)
async def get_animals_by_user_id(user_id: str):
    if exists_id_in_user(user_id):
        animals = db.collection("animals").where("user_id", "==", user_id).get()
        return [animal.to_dict() for animal in animals]
    else:
        raise HTTPException(status_code=404, detail="User not found")


# Register a user
@router.post("/register", status_code=200, response_model=UserCreate)
async def register_user(user: User):
    if exists_email_in_user(user.email):
        raise HTTPException(status_code=401, detail="Email already exists")

    try:
        create_user = pyrebase_auth.create_user_with_email_and_password(
            user.email, user.password
        )
    except HTTPException:
        raise HTTPException(status_code=400, detail="Error creating user")

    try:
        user.id = generate_uuid()
        db.collection("users").document(user.id).set(user.dict())
        # For security, we don't save the password in the database
        # as is handled by Firebase Authentication
        db.collection("users").document(user.id).update({"password": DELETE_FIELD})
        # Send email verification
        pyrebase_auth.send_email_verification(create_user["idToken"])
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login", status_code=200)
async def login_user(email: str, password: str):
    try:
        user_py = pyrebase_auth.sign_in_with_email_and_password(email, password)
        user = firebase_admin_auth.get_user_by_email(email)
        if user.email_verified:
            if not exists_email_in_user(email):
                return JSONResponse(
                    status_code=403, content={"message": "You are not a user"}
                )
            return JSONResponse(status_code=200, content={"token": user_py["idToken"]})
        else:
            raise HTTPException(status_code=401, detail="Email not verified")
    except Exception as e:
        if str(e) == "":
            raise HTTPException(status_code=401, detail="Email not verified")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.put("/{user_id}", status_code=200, response_model=UserUpdateOut)
async def update_user(
    user_id: str, user: UserUpdateIn, email: str = Depends(firebase_authentication)
):
    user_logged = db.collection("users").document(user_id).get().to_dict()
    if exists_id_in_user(user_id):
        if user_logged.email != email:
            raise HTTPException(
                status_code=401, detail="You are not allowed to edit the user"
            )
    else:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.collection("users").document(user_id).update(user.dict())
        user = db.collection("users").document(user_id).get().to_dict()
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Enable user
@router.put("/enable/{user_id}", status_code=200)
async def enable_user(user_id: str, email: str = Depends(firebase_authentication)):
    user_logged = db.collection("users").document(user_id).get().to_dict()
    if exists_id_in_user(user_id):
        if user_logged.email != email:
            raise HTTPException(
                status_code=401, detail="You are not allowed to enable the user"
            )
    else:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.collection("users").document(user_id).update({"active": True})
        return JSONResponse(status_code=200, content={"message": "User enabled"})
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Delete user
@router.delete("/delete/{user_id}", status_code=200)
async def delete_user(user_id: str, email: str = Depends(firebase_authentication)):
    user_logged = db.collection("users").document(user_id).get().to_dict()
    if exists_id_in_user(user_id):
        if user_logged.email != email:
            raise HTTPException(
                status_code=401, detail="You are not allowed to delete the user"
            )
    else:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.collection("users").document(user_id).update({"active": False})
        return JSONResponse(status_code=200, content={"message": "User deleted"})
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
