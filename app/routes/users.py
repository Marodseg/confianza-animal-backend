from fastapi.security import OAuth2PasswordRequestForm
from google.cloud.firestore_v1 import DELETE_FIELD
from starlette.responses import JSONResponse

from app.config.database import db, firebase_admin_auth, pyrebase_auth, storage
from fastapi import APIRouter, HTTPException, Depends, UploadFile

from app.routes.auth import (
    firebase_email_authentication,
    firebase_uid_authentication,
    Token,
)
from app.schemas.animal import AnimalsInDB
from app.schemas.user import User, UserCreate, UserView, UserUpdateIn, UserUpdateOut
from app.utils import (
    exists_email_in_user,
    exists_id_in_user,
)

router = APIRouter()


# Get user with token
@router.get("/me", status_code=200, response_model=UserView)
async def get_user_profile(uid: str = Depends(firebase_uid_authentication)):
    user = db.collection("users").where("id", "==", uid).get()
    if user:
        return UserView(**user[0].to_dict())
    else:
        raise HTTPException(status_code=404, detail="User not found")


# Get user by id
@router.get("/{user_id}", status_code=200, response_model=UserView)
async def get_user_by_id(user_id: str):
    user = db.collection("users").document(user_id).get().to_dict()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Get animals by user id
@router.get("/animals/{user_id}", status_code=200, response_model=AnimalsInDB)
async def get_animals_by_user_id(user_id: str):
    if exists_id_in_user(user_id):
        animals = db.collection("animals").document(user_id).get().to_dict()
        if not animals:
            dogs = []
            cats = []
        else:
            dogs = animals["dogs"]
            cats = animals["cats"]
        return AnimalsInDB(dogs=dogs, cats=cats)
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
        user.id = create_user["localId"]
        db.collection("users").document(user.id).set(user.dict())
        # For security, we don't save the password in the database
        # as is handled by Firebase Authentication
        db.collection("users").document(user.id).update({"password": DELETE_FIELD})
        # Send email verification
        pyrebase_auth.send_email_verification(create_user["idToken"])
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login", status_code=200, response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user_py = pyrebase_auth.sign_in_with_email_and_password(
            form_data.username, form_data.password
        )
        user = firebase_admin_auth.get_user_by_email(form_data.username)

        # Search a user by email in the database
        my_user = (
            db.collection("users")
            .where("email", "==", form_data.username)
            .get()[0]
            .to_dict()
        )

        if user.email_verified:
            if not exists_email_in_user(form_data.username):
                return JSONResponse(
                    status_code=403, content={"message": "You are not a user"}
                )
            if not my_user["active"]:
                return JSONResponse(
                    status_code=401,
                    content={"message": "This user is inactive"},
                )
            return JSONResponse(status_code=200, content={"token": user_py["idToken"]})
        else:
            raise HTTPException(status_code=401, detail="Email not verified")
    except Exception as e:
        if str(e) == "":
            raise HTTPException(status_code=401, detail="Email not verified")
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Enable user
@router.put("/enable", status_code=200)
async def enable_user(uid: str = Depends(firebase_uid_authentication)):
    user = db.collection("users").where("id", "==", uid).get()[0].to_dict()

    if user["active"]:
        raise HTTPException(status_code=400, detail="User already active")

    db.collection("users").document(uid).update({"active": True})

    return JSONResponse(status_code=200, content={"message": "User enabled"})


@router.put("/update/{user_id}", status_code=200, response_model=UserUpdateOut)
async def update_user(
    user_id: str,
    user: UserUpdateIn,
    email: str = Depends(firebase_email_authentication),
):
    user_logged = db.collection("users").document(user_id).get().to_dict()
    if exists_id_in_user(user_id):
        if user_logged["email"] != email:
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


# Disable user
@router.put("/disable", status_code=200)
async def disable_user(uid: str = Depends(firebase_uid_authentication)):
    user = db.collection("users").where("id", "==", uid).get()[0].to_dict()

    if not user["active"]:
        raise HTTPException(status_code=400, detail="User already disabled")

    db.collection("users").document(uid).update({"active": False})
    return JSONResponse(status_code=200, content={"message": "User disabled"})


# Upload photo profile
@router.post("/upload/photo", status_code=200)
async def upload_profile_photo(
    file: UploadFile, email: str = Depends(firebase_email_authentication)
):
    user_logged = db.collection("users").where("email", "==", email).get()
    user = user_logged[0]

    try:
        # Upload a photo to Firebase Storage ensuring that the file is an image
        if file.content_type.startswith("image/"):
            # Get the file extension
            extension = file.filename.split(".")[-1]

            # Generate a random name for the file
            filename = "profile_photo"  # Here we can add the extension
            # But we want to overwrite the previous photo

            # Upload the file and delete the previous one
            storage.child(f"users/{user.id}/{filename}").put(file.file)
            # Get the url of the uploaded file
            url = storage.child(f"users/{user.id}/{filename}").get_url(None)
            # Update the user's photo
            db.collection("users").document(user.id).update({"photo": url})
            return JSONResponse(status_code=200, content={"message": "Photo uploaded"})
        else:
            raise HTTPException(status_code=401, detail="File is not an image")
    except Exception as e:
        raise HTTPException(status_code=401, detail="File is not an image")
