import datetime

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
from app.schemas.enums.petition_status import PetitionStatus
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


# Check if animal is in favorites list of a user
@router.get("/favorites/{animal_id}", status_code=200, response_model=bool)
def check_if_animal_is_in_favorites(
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

    user_dogs_favorites = user["favorites"]["dogs"]
    user_cats_favorites = user["favorites"]["cats"]

    for dog in user_dogs_favorites:
        if dog["id"] == animal_id:
            return True
    for cat in user_cats_favorites:
        if cat["id"] == animal_id:
            return True

    return False


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


# Update user docu
@router.post("/documentation/{petition_id}", status_code=200, response_model=str)
def envy_user_documentation(
    petition_id: str,
    message: str,
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

    petitions = db_a.collection("petitions").where("user_id", "==", uid_a).get()
    for petition in petitions:
        if (
            petition.id == petition_id
            and petition.to_dict()["status"] == PetitionStatus.info_approved
        ):
            db_a.collection("petitions").document(petition.id).update(
                {
                    "status": PetitionStatus.docu_envied,
                    "user_message": message,
                    "status_date": datetime.datetime.now(),
                }
            )
            return JSONResponse(
                status_code=200, content={"message": "User documentation envied"}
            )
    return HTTPException(status_code=404, detail="Documentation can not be envied")


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
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Enable user
@router.post("/enable", status_code=200)
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


# Update user docu
@router.post("/update-documentation/{petition_id}", status_code=200, response_model=str)
def update_user_documentation(
    petition_id: str,
    message: str,
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

    petitions = db_a.collection("petitions").where("user_id", "==", uid_a).get()
    for petition in petitions:
        if (
            petition.to_dict()["status"] != PetitionStatus.rejected
            and petition.to_dict()["status"] != PetitionStatus.accepted
            and petition.to_dict()["status"] != PetitionStatus.initiated
        ) and (
            petition.to_dict()["status"] == PetitionStatus.docu_pending
            or petition.to_dict()["status"] == PetitionStatus.docu_changed
            or petition.to_dict()["status"] == PetitionStatus.docu_envied
            or petition.to_dict()["status"] == PetitionStatus.docu_rejected
        ):
            db_a.collection("petitions").document(petition.id).update(
                {
                    "status": PetitionStatus.docu_changed,
                    "user_message": message,
                    "status_date": datetime.datetime.now(),
                }
            )
            return JSONResponse(
                status_code=200, content={"message": "User documentation updated"}
            )
    raise HTTPException(status_code=404, detail="User documentation can't be updated")


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
    # Check if the info changed to update the petition
    info_user_changed = False

    if user.name:
        old_user["name"] = user.name

    if user.photo:
        old_user["photo"] = user.photo

    if user.home_type:
        old_user["home_type"] = user.home_type
        info_user_changed = True

    if user.free_time:
        old_user["free_time"] = user.free_time
        info_user_changed = True

    if user.previous_experience:
        old_user["previous_experience"] = user.previous_experience
        info_user_changed = True

    if user.frequency_travel:
        old_user["frequency_travel"] = user.frequency_travel
        info_user_changed = True

    if user.kids:
        old_user["kids"] = user.kids
        info_user_changed = True

    if user.other_animals:
        old_user["other_animals"] = user.other_animals
        info_user_changed = True

    try:
        db_a.collection("users").document(old_user["id"]).update(old_user)
        user = db_a.collection("users").document(old_user["id"]).get().to_dict()

        petitions = (
            db_a.collection("petitions").where("user_id", "==", user["id"]).get()
        )
        if info_user_changed:
            for petition in petitions:
                if (
                    (
                        user["home_type"]
                        and (user["home_type"] != petition.to_dict()["home_type"])
                    )
                    or (
                        user["free_time"]
                        and (user["free_time"] != petition.to_dict()["free_time"])
                    )
                    or (
                        user["previous_experience"]
                        and (
                            user["previous_experience"]
                            != petition.to_dict()["previous_experience"]
                        )
                    )
                    or (
                        user["frequency_travel"]
                        and (
                            user["frequency_travel"]
                            != petition.to_dict()["frequency_travel"]
                        )
                    )
                    or (user["kids"] and (user["kids"] != petition.to_dict()["kids"]))
                    or (
                        user["other_animals"]
                        and (
                            user["other_animals"] != petition.to_dict()["other_animals"]
                        )
                    )
                ):
                    if petition.to_dict()["status"] == PetitionStatus.info_rejected:
                        db_a.collection("petitions").document(petition.id).update(
                            {
                                "status": PetitionStatus.info_changed,
                                "home_type_bool": False,
                                "free_time_bool": False,
                                "previous_experience_bool": False,
                                "frequency_travel_bool": False,
                                "kids_bool": False,
                                "other_animals_bool": False,
                                "status_date": datetime.datetime.now(),
                                "user_message": "Información del usuario modificada",
                                "home_type": user["home_type"],
                                "free_time": user["free_time"],
                                "previous_experience": user["previous_experience"],
                                "frequency_travel": user["frequency_travel"],
                                "kids": user["kids"],
                                "other_animals": user["other_animals"],
                            }
                        )
                    elif (
                        petition.to_dict()["status"] != PetitionStatus.accepted
                        and petition.to_dict()["status"] != PetitionStatus.rejected
                        and petition.to_dict()["status"] != PetitionStatus.initiated
                    ):
                        db_a.collection("petitions").document(petition.id).update(
                            {
                                "status": PetitionStatus.info_pending,
                                "home_type_bool": False,
                                "free_time_bool": False,
                                "previous_experience_bool": False,
                                "frequency_travel_bool": False,
                                "kids_bool": False,
                                "other_animals_bool": False,
                                "status_date": datetime.datetime.now(),
                                "user_message": "Información del usuario modificada",
                                "home_type": user["home_type"],
                                "free_time": user["free_time"],
                                "previous_experience": user["previous_experience"],
                                "frequency_travel": user["frequency_travel"],
                                "kids": user["kids"],
                                "other_animals": user["other_animals"],
                            }
                        )
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Disable user
@router.delete("/disable", status_code=200)
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
