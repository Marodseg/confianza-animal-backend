import uuid
from typing import Union

from app.config.database import db, db_test
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size


def exists_email_in_organization(email: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    return db_a.collection("organizations").where("email", "==", email).get()


def exists_phone_in_organization(phone: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    return db_a.collection("organizations").where("phone", "==", phone).get()


def exists_name_in_organization(name: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    return db_a.collection("organizations").where("name", "==", name).get()


def exists_email_in_user(email: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    return db_a.collection("users").where("email", "==", email).get()


def exists_id_in_user(user_id: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    return db_a.collection("users").where("id", "==", user_id).get()


def exists_dog_in_animals(dog_id: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    dogs = db_a.collection("animals").document("animals").get().to_dict()["dogs"]
    for dog in dogs:
        if dog["id"] == dog_id:
            return True
    return False


def exists_cat_in_animals(cat_id: str, test_db: bool = False) -> bool:
    if test_db is True:
        db_a = db_test
    else:
        db_a = db
    cats = db_a.collection("animals").document("animals").get().to_dict()["cats"]
    for cat in cats:
        if cat["id"] == cat_id:
            return True
    return False


def get_dog_or_cat_by_filters(
    animals: [],
    province: Province = None,
    size: Size = None,
    raze: Union[CatRaze, DogRaze] = None,
    years: int = None,
    greater_or_equal: bool = True,
    gender: Gender = None,
    activity: Activity = None,
    is_urgent: bool = None,
):
    if animals:
        if province is not None:
            animals = [animal for animal in animals if animal["zone"] == province]
        if size is not None:
            animals = [animal for animal in animals if animal["size"] == size]
        if raze is not None:
            animals = [animal for animal in animals if animal["raze"] == raze]
        if years is not None:
            if greater_or_equal:
                animals = [animal for animal in animals if animal["years"] >= years]
            else:
                animals = [animal for animal in animals if animal["years"] <= years]
        if gender is not None:
            animals = [animal for animal in animals if animal["gender"] == gender]
        if activity is not None:
            animals = [
                animal for animal in animals if animal["activity_level"] == activity
            ]
        if is_urgent is not None:
            animals = [animal for animal in animals if animal["is_urgent"] == is_urgent]

    return animals


def generate_uuid() -> str:
    return str(uuid.uuid4().hex)
