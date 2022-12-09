from app.routes.filters import (
    get_provinces,
    get_gender,
    get_activity,
    get_size,
    get_cat_raze,
    get_dog_raze,
    get_all,
)
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size


def test_get_provinces():
    provinces = get_provinces()
    assert provinces == [province.value for province in Province]


def test_get_gender():
    genders = get_gender()
    assert genders == [gender.value for gender in Gender]


def test_get_activity():
    activities = get_activity()
    assert activities == [activity.value for activity in Activity]


def test_get_size():
    sizes = get_size()
    assert sizes == [size.value for size in Size]


def test_get_cat_raze():
    cat_razes = get_cat_raze()
    assert cat_razes == [raze.value for raze in CatRaze]


def test_get_dog_raze():
    dog_razes = get_dog_raze()
    assert dog_razes == [raze.value for raze in DogRaze]


def test_get_all():
    all_filters = get_all()
    assert all_filters == {
        "provinces": [province.value for province in Province],
        "gender": [gender.value for gender in Gender],
        "activity": [activity.value for activity in Activity],
        "size": [size.value for size in Size],
        "cat_raze": [raze.value for raze in CatRaze],
        "dog_raze": [raze.value for raze in DogRaze],
    }
