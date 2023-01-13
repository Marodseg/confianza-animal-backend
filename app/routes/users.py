from typing import List, Union

from fastapi.security import OAuth2PasswordRequestForm
from google.cloud.firestore_v1 import DELETE_FIELD
from starlette.responses import JSONResponse

from app.config.database import (
    db,
    db_test,
    firebase_admin_auth,
    pyrebase_auth,
    storage,
    test_storage,
    test_pyrebase_auth,
)
from fastapi import APIRouter, HTTPException, Depends, UploadFile

from app.routes.auth import (
    firebase_email_authentication,
    firebase_uid_authentication,
    Token,
)
from app.schemas.animal import Dog, Cat, AnimalsInDB
from app.schemas.user import User, UserCreate, UserView, UserUpdateIn, UserUpdateOut
from app.utils import (
    exists_email_in_user,
)

router = APIRouter()


# Get user with token
@router.get("/me", status_code=200, response_model=UserView)
def get_user_profile(
    uid: str = Depends(firebase_uid_authentication), test_db: bool = False
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    user = db_a.collection("users").where("id", "==", uid_a).get()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserView(**user[0].to_dict())


# Get user favorites list
@router.get("/favorites", status_code=200, response_model=dict)
def get_user_favorites(
    uid: str = Depends(firebase_uid_authentication), test_db: bool = False
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    user = db_a.collection("users").where("id", "==", uid_a).get()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "dogs": user[0].to_dict()["favorites"]["dogs"],
        "cats": user[0].to_dict()["favorites"]["cats"],
    }


# Get user by id
@router.get("/{user_id}", status_code=200, response_model=UserView)
def get_user_by_id(user_id: str, test_db: bool = False):
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    user = db_a.collection("users").document(user_id).get().to_dict()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Get animals by user id (NOT USED YET)
# @router.get("/animals/{user_id}", status_code=200, response_model=AnimalsInDB)
# def get_animals_by_user_id(user_id: str, test_db: bool = False):
#     if test_db is True:
#         db_a = db_test
#     else:
#         db_a = db
#     if exists_id_in_user(user_id, test_db):
#         animals = db_a.collection("animals").document(user_id).get().to_dict()
#         if not animals:
#             dogs = []
#             cats = []
#         else:
#             dogs = animals["dogs"]
#             cats = animals["cats"]
#         return AnimalsInDB(dogs=dogs, cats=cats)
#     else:
#         raise HTTPException(status_code=404, detail="User not found")


# Post user favorite animal
@router.post("/favorites/{animal_id}", status_code=200, response_model=dict)
def post_user_favorites(
    animal_id: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    user = db_a.collection("users").where("id", "==", uid_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    favorite_dog = None
    favorite_cat = None

    for animal in animals["dogs"]:
        if animal["id"] == animal_id:
            favorite_dog = animal

    if favorite_dog is None:
        for animal in animals["cats"]:
            if animal["id"] == animal_id:
                favorite_cat = animal

    if favorite_cat is None and favorite_dog is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    user_favorites_dogs = user["favorites"]["dogs"]
    user_favorites_cats = user["favorites"]["cats"]

    if favorite_dog is not None:
        for dog in user_favorites_dogs:
            if dog["id"] == favorite_dog["id"]:
                raise HTTPException(
                    status_code=400, detail="Animal already in favorites"
                )

    if favorite_cat is not None:
        for cat in user_favorites_cats:
            if cat["id"] == favorite_cat["id"]:
                raise HTTPException(
                    status_code=400, detail="Animal already in favorites"
                )

    if favorite_dog is not None:
        user_favorites_dogs.append(favorite_dog)
    else:
        user_favorites_cats.append(favorite_cat)

    db_a.collection("users").document(uid_a).update(
        {"favorites": {"dogs": user_favorites_dogs, "cats": user_favorites_cats}}
    )

    user_with_favorites = (
        db_a.collection("users").where("id", "==", uid_a).get()[0].to_dict()
    )

    return user_with_favorites["favorites"]


# Register a user
@router.post("/register", status_code=200, response_model=UserCreate)
def register_user(user: User, test_db: bool = False):
    if test_db is True:
        db_a = db_test
        p_auth = test_pyrebase_auth
    else:
        db_a = db
        p_auth = pyrebase_auth

    if exists_email_in_user(user.email, test_db):
        raise HTTPException(status_code=401, detail="Email already exists")

    try:
        create_user = p_auth.create_user_with_email_and_password(
            user.email, user.password
        )
    except HTTPException:
        raise HTTPException(status_code=400, detail="Error creating user")

    try:
        user.id = create_user["localId"]
        db_a.collection("users").document(user.id).set(user.dict())
        # For security, we don't save the password in the database
        # as is handled by Firebase Authentication
        db_a.collection("users").document(user.id).update({"password": DELETE_FIELD})
        # Send email verification
        p_auth.send_email_verification(create_user["idToken"])
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login", status_code=200, response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
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
                raise HTTPException(status_code=404, detail="User not found")
            if not my_user["active"]:
                raise HTTPException(status_code=403, detail="User not active")
            return JSONResponse(status_code=200, content={"token": user_py["idToken"]})
        else:
            raise HTTPException(status_code=400, detail="Email not verified")
    except Exception as e:
        if str(e) == "":
            raise HTTPException(status_code=400, detail="Email not verified")
        raise HTTPException(status_code=400, detail="Invalid credentials")


# Enable user
@router.put("/enable", status_code=200)
def enable_user(uid: str = Depends(firebase_uid_authentication), test_db: bool = False):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    user = db_a.collection("users").where("id", "==", uid_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_a.collection("users").document(uid_a).update({"active": True})

    return JSONResponse(status_code=200, content={"message": "User enabled"})


@router.put("/update", status_code=200, response_model=UserUpdateOut)
def update_user(
    user: UserUpdateIn,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    my_user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user or not my_user:
        raise HTTPException(status_code=404, detail="User not found")

    # We keep a copy of the old user
    old_user = my_user.copy()

    if user.name:
        old_user["name"] = user.name

    try:
        db_a.collection("users").document(old_user["id"]).update(old_user)
        user = db_a.collection("users").document(old_user["id"]).get().to_dict()
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Disable user
@router.put("/disable", status_code=200)
def disable_user(
    uid: str = Depends(firebase_uid_authentication), test_db: bool = False
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    user = db_a.collection("users").where("id", "==", uid_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_a.collection("users").document(uid_a).update({"active": False})
    return JSONResponse(status_code=200, content={"message": "User disabled"})


# Upload photo profile
@router.post("/upload/photo", status_code=200)
def upload_profile_photo(
    file: UploadFile,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        storage_a = test_storage
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        storage_a = storage
        email_a = email
    user_logged = db_a.collection("users").where("email", "==", email_a).get()

    if not user_logged:
        raise HTTPException(status_code=404, detail="User not found")

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
            storage_a.child(f"users/{user.id}/{filename}").put(file.file)
            # Get the url of the uploaded file
            url = storage_a.child(f"users/{user.id}/{filename}").get_url(None)
            # Update the user's photo
            db_a.collection("users").document(user.id).update({"photo": url})
            return JSONResponse(status_code=200, content={"message": "Photo uploaded"})
        else:
            raise HTTPException(status_code=401, detail="File is not an image")
    except Exception as e:
        raise HTTPException(status_code=401, detail="File is not an image")


# Delete favorite
@router.delete("/favorites/{animal_id}", status_code=200, response_model=str)
def delete_favorite(
    animal_id: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    user = db_a.collection("users").where("id", "==", uid_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dog_favorites = user["favorites"]["dogs"]
    cat_favorites = user["favorites"]["cats"]
    removed = False

    for dog in dog_favorites:
        if dog["id"] == animal_id:
            dog_favorites.remove(dog)
            removed = True

    for cat in cat_favorites:
        if cat["id"] == animal_id:
            cat_favorites.remove(cat)
            removed = True

    if not removed:
        raise HTTPException(
            status_code=404, detail="The animal is not in the favorites list"
        )

    db_a.collection("users").document(uid_a).update(
        {"favorites": {"dogs": dog_favorites, "cats": cat_favorites}}
    )

    return JSONResponse(status_code=200, content={"message": "Favorite deleted"})
