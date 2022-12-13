from typing import List, Optional

from starlette.responses import JSONResponse

from app.config.database import db, db_test, storage, test_storage
from fastapi import APIRouter, HTTPException, UploadFile, Depends

from app.routes.auth import firebase_uid_authentication
from app.schemas.animal import Dog, Cat, AnimalsInDB
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.utils import get_dog_or_cat_by_filters

router = APIRouter()


# Get all animals
@router.get("/", status_code=200, response_model=Optional[AnimalsInDB])
def get_all_animals(test_db=False):
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    animals = db_a.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]
    cats = animals["cats"]
    return AnimalsInDB(dogs=dogs, cats=cats)


# Get dog by id
@router.get("/dog/{dog_id}", status_code=200, response_model=Dog)
def get_dog_by_id(dog_id: str, test_db=False):
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    animals = db_a.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]
    dog = next((dog for dog in dogs if dog["id"] == dog_id), None)
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    return dog


# Get cat by id
@router.get("/cat/{cat_id}", status_code=200, response_model=Cat)
def get_cat_by_id(cat_id: str, test_db=False):
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    animals = db_a.collection("animals").document("animals").get().to_dict()
    cats = animals["cats"]
    cat = next((cat for cat in cats if cat["id"] == cat_id), None)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")

    return cat


# Get dog by all filters
@router.get("/dog", status_code=200, response_model=Optional[List[Dog]])
def get_dog_by_filters(
    province: Province = None,
    size: Size = None,
    raze: DogRaze = None,
    age: int = None,
    greater_or_equal: bool = True,
    gender: Gender = None,
    activity: Activity = None,
    is_urgent: bool = None,
    test_db=False,
):
    if test_db is True:
        db_a = db_test
    else:
        db_a = db

    # By default, the parameter greater_or_equal is True
    # and means that the age of the dog must be greater or equal to the age passed as a parameter
    # If greater_or_equal is False, the age of the dog must be less or equal to the age passed as a parameter

    animals = db_a.collection("animals").document("animals").get().to_dict()
    if animals is None:
        return []
    if animals["dogs"] is None:
        return []
    dogs = animals["dogs"]
    if not dogs:
        return []
    return get_dog_or_cat_by_filters(
        dogs, province, size, raze, age, greater_or_equal, gender, activity, is_urgent
    )


# Get cat by all filters
@router.get("/cat", status_code=200, response_model=Optional[List[Cat]])
def get_cat_by_filters(
    province: Province = None,
    size: Size = None,
    raze: CatRaze = None,
    age: int = None,
    greater_or_equal: bool = True,
    gender: Gender = None,
    activity: Activity = None,
    is_urgent: bool = None,
    test_db=False,
):
    if test_db is True:
        db_a = db_test
    else:
        db_a = db

    # By default, the parameter greater_or_equal is True
    # and means that the age of the cat must be greater or equal to the age passed as a parameter
    # If greater_or_equal is False, the age of the cat must be less or equal to the age passed as a parameter

    animals = db_a.collection("animals").document("animals").get().to_dict()
    if animals is None:
        return []
    if animals["cats"] is None:
        return []
    cats = animals["cats"]

    return get_dog_or_cat_by_filters(
        cats, province, size, raze, age, greater_or_equal, gender, activity, is_urgent
    )


@router.post("/dog/{dog_id}/photos", status_code=200)
def upload_dog_photos(
    dog_id: str,
    photos: List[UploadFile],
    uid: str = Depends(firebase_uid_authentication),
    test_db=False,
):
    if test_db is True:
        db_a = db_test
        storage_a = test_storage
        uid_a = (
            db_a.collection("organizations").document("TEST USER").get().to_dict()["id"]
        )
    else:
        db_a = db
        storage_a = storage
        uid_a = uid

    my_org = (
        db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()
    )

    if not my_org:
        raise HTTPException(status_code=403, detail="You are not an organization")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]

    for dog in dogs:
        if dog["id"] == dog_id:
            if dog["organization_name"] != my_org["name"]:
                raise HTTPException(
                    status_code=403, detail="You are not the owner of this dog"
                )

            for photo in photos:
                if not photo.content_type.startswith("image/"):
                    raise HTTPException(status_code=400, detail="Not an image")
                filename = storage_a.child(f"dogs/{dog_id}/{photo.filename}").put(
                    photo.file
                )
                url = storage_a.child(filename["name"]).get_url(None)

                if url not in dog["photos"]:
                    dog["photos"].append(url)

            db_a.collection("animals").document("animals").set(
                {"dogs": dogs}, merge=True
            )
            db_a.collection("organizations").document(my_org["name"]).set(
                {"dogs": dogs},
                merge=True,
            )

            petitions = db_a.collection("petitions").get()
            for petition in petitions:
                if petition.to_dict()["dog"]:
                    if petition.to_dict()["dog"]["id"] == dog_id:
                        db_a.collection("petitions").document(petition.id).update(
                            {"dog": dog}
                        )

            return JSONResponse(
                status_code=200, content={"message": "Photos uploaded successfully"}
            )

    raise HTTPException(status_code=404, detail="Error uploading photos")


@router.post("/cat/{cat_id}/photos", status_code=200)
def upload_cat_photos(
    cat_id: str,
    photos: List[UploadFile],
    uid: str = Depends(firebase_uid_authentication),
    test_db=False,
):
    if test_db is True:
        db_a = db_test
        storage_a = test_storage
        uid_a = (
            db_a.collection("organizations").document("TEST USER").get().to_dict()["id"]
        )
    else:
        db_a = db
        storage_a = storage
        uid_a = uid

    my_org = (
        db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()
    )

    if not my_org:
        raise HTTPException(status_code=403, detail="You are not an organization")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    cats = animals["cats"]

    for cat in cats:
        if cat["id"] == cat_id:
            if cat["organization_name"] != my_org["name"]:
                raise HTTPException(
                    status_code=403, detail="You are not the owner of this cat"
                )

            for photo in photos:
                if not photo.content_type.startswith("image/"):
                    raise HTTPException(status_code=400, detail="Not an image")
                filename = storage_a.child(f"cats/{cat_id}/{photo.filename}").put(
                    photo.file
                )
                url = storage_a.child(filename["name"]).get_url(None)

                if url not in cat["photos"]:
                    cat["photos"].append(url)

            db_a.collection("animals").document("animals").update({"cats": cats})
            db_a.collection("organizations").document(my_org["name"]).update(
                {"cats": cats}
            )

            petitions = db_a.collection("petitions").get()
            for petition in petitions:
                if petition.to_dict()["cat"]:
                    if petition.to_dict()["cat"]["id"] == cat_id:
                        db_a.collection("petitions").document(petition.id).update(
                            {"cat": cat}
                        )

            return JSONResponse(
                status_code=200, content={"message": "Photos uploaded successfully"}
            )

    raise HTTPException(status_code=404, detail="Error uploading photos")


# Delete photo from dog
@router.delete("/dog/{dog_id}/photo", status_code=200)
def delete_dog_photo(
    dog_id: str,
    photo_url: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db=False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations").document("TEST USER").get().to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid

    my_org = (
        db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()
    )

    if not my_org:
        raise HTTPException(status_code=403, detail="You are not an organization")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]

    for dog in dogs:
        if dog["id"] == dog_id:
            if dog["organization_name"] != my_org["name"]:
                raise HTTPException(
                    status_code=403, detail="You are not the owner of this dog"
                )

            if photo_url not in dog["photos"]:
                raise HTTPException(status_code=404, detail="Photo not found")

            dog["photos"].remove(photo_url)
            db_a.collection("animals").document("animals").set(
                {"dogs": dogs}, merge=True
            )
            db_a.collection("organizations").document(my_org["name"]).set(
                {"dogs": dogs},
                merge=True,
            )

            petitions = db_a.collection("petitions").get()
            for petition in petitions:
                if petition.to_dict()["dog"]:
                    if petition.to_dict()["dog"]["id"] == dog_id:
                        db_a.collection("petitions").document(petition.id).update(
                            {"dog": dog}
                        )

            return JSONResponse(
                status_code=200, content={"message": "Photo deleted successfully"}
            )

    raise HTTPException(status_code=404, detail="Error deleting photo")


# Delete photo from cat
@router.delete("/cat/{cat_id}/photo", status_code=200)
def delete_cat_photo(
    cat_id: str,
    photo_url: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db=False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations").document("TEST USER").get().to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid

    my_org = (
        db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()
    )

    if not my_org:
        raise HTTPException(status_code=403, detail="You are not an organization")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    cats = animals["cats"]

    for cat in cats:
        if cat["id"] == cat_id:
            if cat["organization_name"] != my_org["name"]:
                raise HTTPException(
                    status_code=403, detail="You are not the owner of this cat"
                )

            if photo_url not in cat["photos"]:
                raise HTTPException(status_code=404, detail="Photo not found")

            cat["photos"].remove(photo_url)
            db_a.collection("animals").document("animals").update({"cats": cats})
            db_a.collection("organizations").document(my_org["name"]).update(
                {"cats": cats}
            )

            petitions = db_a.collection("petitions").get()
            for petition in petitions:
                if petition.to_dict()["cat"]:
                    if petition.to_dict()["cat"]["id"] == cat_id:
                        db_a.collection("petitions").document(petition.id).update(
                            {"cat": cat}
                        )

            return JSONResponse(
                status_code=200, content={"message": "Photo deleted successfully"}
            )

    raise HTTPException(status_code=404, detail="Error deleting photo")


# Delete dog
@router.delete("/dog/{dog_id}", status_code=200)
def delete_dog_by_id(
    dog_id: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db=False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations").document("TEST USER").get().to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid

    my_org = (
        db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()
    )

    if not my_org:
        raise HTTPException(status_code=403, detail="You are not an organization")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]

    for dog in dogs:
        if dog["id"] == dog_id:
            if dog["organization_name"] != my_org["name"]:
                raise HTTPException(
                    status_code=403, detail="You are not the owner of this dog"
                )

            dogs.remove(dog)
            db_a.collection("animals").document("animals").set(
                {"dogs": dogs}, merge=True
            )
            db_a.collection("organizations").document(my_org["name"]).set(
                {"dogs": dogs},
                merge=True,
            )
            return JSONResponse(
                status_code=200, content={"message": "Dog deleted successfully"}
            )

    raise HTTPException(status_code=404, detail="Error deleting dog")


# Delete cat
@router.delete("/cat/{cat_id}", status_code=200)
def delete_cat_by_id(
    cat_id: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db=False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations").document("TEST USER").get().to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid

    my_org = (
        db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()
    )

    if not my_org:
        raise HTTPException(status_code=403, detail="You are not an organization")

    animals = db_a.collection("animals").document("animals").get().to_dict()
    cats = animals["cats"]

    for cat in cats:
        if cat["id"] == cat_id:
            if cat["organization_name"] != my_org["name"]:
                raise HTTPException(
                    status_code=403, detail="You are not the owner of this cat"
                )

            cats.remove(cat)
            db_a.collection("animals").document("animals").update({"cats": cats})
            db_a.collection("organizations").document(my_org["name"]).update(
                {"cats": cats}
            )
            return JSONResponse(
                status_code=200, content={"message": "Cat deleted successfully"}
            )

    raise HTTPException(status_code=404, detail="Error deleting cat")
