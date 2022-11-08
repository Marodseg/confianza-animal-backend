from typing import List

from fastapi import APIRouter

from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size

router = APIRouter()


# Get provinces enum
@router.get("/provinces", status_code=200, response_model=List[str])
async def get_provinces():
    return [province.value for province in Province]


# Get gender enum
@router.get("/gender", status_code=200, response_model=List[str])
async def get_gender():
    return [gender.value for gender in Gender]


# Get activity level enum
@router.get("/activity", status_code=200, response_model=List[str])
async def get_activity():
    return [activity.value for activity in Activity]


# Get size enum
@router.get("/size", status_code=200, response_model=List[str])
async def get_size():
    return [size.value for size in Size]


# Get cat raze enum
@router.get("/cat-raze", status_code=200, response_model=List[str])
async def get_cat_raze():
    return [raze.value for raze in CatRaze]


# Get dog raze enum
@router.get("/dog-raze", status_code=200, response_model=List[str])
async def get_dog_raze():
    return [raze.value for raze in DogRaze]


# Get all enums
@router.get("/all", status_code=200, response_model=dict)
async def get_all():
    return {
        "provinces": [province.value for province in Province],
        "gender": [gender.value for gender in Gender],
        "activity": [activity.value for activity in Activity],
        "size": [size.value for size in Size],
        "cat_raze": [raze.value for raze in CatRaze],
        "dog_raze": [raze.value for raze in DogRaze],
    }
