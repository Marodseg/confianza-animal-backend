import uuid
from typing import Union

from app.config.database import db
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size


def exists_email_in_organization(email: str) -> bool:
    return db.collection("organizations").where("email", "==", email).get()


def exists_phone_in_organization(phone: str) -> bool:
    return db.collection("organizations").where("phone", "==", phone).get()


def exists_name_in_organization(name: str) -> bool:
    return db.collection("organizations").where("name", "==", name).get()


def exists_email_in_user(email: str) -> bool:
    return db.collection("users").where("email", "==", email).get()


def exists_phone_in_user(phone: str) -> bool:
    return db.collection("users").where("phone", "==", phone).get()


def exists_id_in_user(user_id: str) -> bool:
    return db.collection("users").where("id", "==", user_id).get()


def exists_dog_in_animals(dog_id: str) -> bool:
    return (
        db.collection("animals")
        .document("animals")
        .get()
        .to_dict()["dogs"]
        .where("id", "==", dog_id)
        .get()
    )


def exists_cat_in_animals(cat_id: str) -> bool:
    return (
        db.collection("animals")
        .document("animals")
        .get()
        .to_dict()["cats"]
        .where("id", "==", cat_id)
        .get()
    )


def get_dog_or_cat_by_filters(
    animals: [],
    zone: Province = None,
    size: Size = None,
    raze: Union[CatRaze, DogRaze] = None,
    age: int = None,
    greater_or_equal: bool = True,
    gender: Gender = None,
    activity: Activity = None,
    is_urgent: bool = None,
):
    if animals:
        if zone:
            animals = [animal for animal in animals if animal["zone"] == zone]
        if size:
            animals = [animal for animal in animals if animal["size"] == size]
        if raze:
            animals = [animal for animal in animals if animal["raze"] == raze]
        if age:
            if greater_or_equal:
                animals = [animal for animal in animals if animal["age"] >= age]
            else:
                animals = [animal for animal in animals if animal["age"] <= age]
        if gender:
            animals = [animal for animal in animals if animal["gender"] == gender]
        if activity:
            animals = [animal for animal in animals if animal["activity"] == activity]
        if is_urgent:
            animals = [animal for animal in animals if animal["is_urgent"] == is_urgent]

        return animals


def generate_uuid() -> str:
    return str(uuid.uuid4())
