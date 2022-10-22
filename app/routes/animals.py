from typing import List, Optional

from app.config.database import db
from fastapi import APIRouter, HTTPException

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
@router.get("/", status_code=200, response_model=AnimalsInDB)
async def get_all_animals():
    animals = db.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]
    cats = animals["cats"]
    return AnimalsInDB(dogs=dogs, cats=cats)


# Get dog by id
@router.get("/dog/{dog_id}", status_code=200, response_model=Dog)
async def get_dog_by_id(dog_id: str):
    animals = db.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]
    dog = next((dog for dog in dogs if dog["id"] == dog_id), None)
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    return dog


# Get cat by id
@router.get("/cat/{cat_id}", status_code=200, response_model=Cat)
async def get_cat_by_id(cat_id: str):
    animals = db.collection("animals").document("animals").get().to_dict()
    cats = animals["cats"]
    cat = next((cat for cat in cats if cat["id"] == cat_id), None)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")

    return cat


# Get dog by all filters
@router.get("/dog", status_code=200, response_model=Optional[List[Dog]])
async def get_dog_by_filters(
    zone: Province = None,
    size: Size = None,
    raze: DogRaze = None,
    age: int = None,
    greater_or_equal: bool = True,
    gender: Gender = None,
    activity: Activity = None,
    is_urgent: bool = None,
):

    # By default, the parameter greater_or_equal is True
    # and means that the age of the dog must be greater or equal to the age passed as a parameter
    # If greater_or_equal is False, the age of the dog must be less or equal to the age passed as a parameter

    animals = db.collection("animals").document("animals").get().to_dict()
    dogs = animals["dogs"]
    return get_dog_or_cat_by_filters(
        dogs, zone, size, raze, age, greater_or_equal, gender, activity, is_urgent
    )


# Get cat by all filters
@router.get("/cat", status_code=200, response_model=Optional[List[Cat]])
async def get_cat_by_filters(
    zone: Province = None,
    size: Size = None,
    raze: CatRaze = None,
    age: int = None,
    greater_or_equal: bool = True,
    gender: Gender = None,
    activity: Activity = None,
    is_urgent: bool = None,
):

    # By default, the parameter greater_or_equal is True
    # and means that the age of the cat must be greater or equal to the age passed as a parameter
    # If greater_or_equal is False, the age of the cat must be less or equal to the age passed as a parameter

    animals = db.collection("animals").document("animals").get().to_dict()
    cats = animals["cats"]

    return get_dog_or_cat_by_filters(
        cats, zone, size, raze, age, greater_or_equal, gender, activity, is_urgent
    )
