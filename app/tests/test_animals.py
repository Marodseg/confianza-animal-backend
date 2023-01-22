from io import BytesIO

import pytest
from fastapi import UploadFile, HTTPException

from app.routes.animals import (
    get_all_animals,
    get_dog_by_id,
    get_cat_by_id,
    get_dog_by_filters,
    get_cat_by_filters,
    upload_dog_photos,
    delete_dog_photo,
    upload_cat_photos,
    delete_cat_photo,
    delete_dog_by_id,
    delete_cat_by_id,
)
from app.routes.organizations import post_cat, post_dog
from app.schemas.animal import Dog, Cat
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.tests.conftest import delete_dog_by_name, delete_cat_by_name


def test_get_all_animals():
    # Let's add a dog and a cat to the database
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    post_cat(cat, test_db=True)

    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    post_dog(dog, test_db=True)

    animals = get_all_animals(test_db=True)
    assert animals is not None
    assert animals.dogs[0].raze == DogRaze.chihuahua
    assert animals.dogs[0].name == "Prueba"
    assert animals.cats[0].raze == CatRaze.persa
    assert animals.cats[0].name == "Prueba"
    # Delete dog and cat from database
    delete_dog_by_name("Prueba")
    delete_cat_by_name("Prueba")


def test_get_dog_by_id():
    # Let's add a dog to the database
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    post_dog(dog, test_db=True)
    dog_by_function = get_dog_by_id(dog.id, test_db=True)
    assert dog_by_function is not None
    assert dog_by_function["raze"] == DogRaze.chihuahua
    assert dog_by_function["name"] == "Prueba"
    # Delete dog from database
    delete_dog_by_name("Prueba")


def test_get_cat_by_id():
    # Let's add a cat to the database
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    post_cat(cat, test_db=True)
    cat_by_function = get_cat_by_id(cat.id, test_db=True)
    assert cat_by_function is not None
    assert cat_by_function["raze"] == CatRaze.persa
    assert cat_by_function["name"] == "Prueba"
    # Delete cat from database
    delete_cat_by_name("Prueba")


def test_get_dog_by_filters():
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    post_dog(dog, test_db=True)

    dog2 = Dog(
        name="Prueba 2",
        years=1,
        gender=Gender.female,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.mini,
        zone=Province.granada,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.medium,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.akita,
    )

    post_dog(dog2, test_db=True)
    dogs = get_dog_by_filters(size=Size.mini, province=Province.granada, test_db=True)
    assert dogs is not None
    assert dogs[0]["raze"] == DogRaze.akita
    assert dogs[0]["name"] == "Prueba 2"
    dogs = get_dog_by_filters(size=Size.small, province=Province.alava, test_db=True)
    assert dogs is not None
    assert dogs[0]["raze"] == DogRaze.chihuahua
    assert dogs[0]["name"] == "Prueba"
    dogs = get_dog_by_filters(size=Size.big, province=Province.alava, test_db=True)
    assert dogs == []
    # Delete dogs from database
    delete_dog_by_name("Prueba")
    delete_dog_by_name("Prueba 2")


def test_get_cat_by_filters():
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    post_cat(cat, test_db=True)

    cat2 = Cat(
        name="Prueba 2",
        years=1,
        gender=Gender.female,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.mini,
        zone=Province.granada,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.high,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.bengal,
    )

    post_cat(cat2, test_db=True)
    cats = get_cat_by_filters(size=Size.mini, province=Province.granada, test_db=True)
    assert cats is not None
    assert cats[0]["raze"] == CatRaze.bengal
    assert cats[0]["name"] == "Prueba 2"
    cats = get_cat_by_filters(size=Size.small, province=Province.alava, test_db=True)
    assert cats is not None
    assert cats[0]["raze"] == CatRaze.persa
    assert cats[0]["name"] == "Prueba"
    cats = get_cat_by_filters(size=Size.big, province=Province.alava, test_db=True)
    assert cats == []
    # Delete cats from database
    delete_cat_by_name("Prueba")
    delete_cat_by_name("Prueba 2")


def test_upload_dog_photos(login_org):
    # Create an object of type UploadFile to be able to upload it
    file1 = UploadFile(
        filename="image.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    file2 = UploadFile(
        filename="image2.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    post_dog(dog, test_db=True)
    upload_dog_photos(dog.id, [file1, file2], test_db=True)
    dog = get_dog_by_id(dog.id, test_db=True)
    assert len(dog["photos"]) == 2

    # Let's delete the photos from the database
    delete_dog_photo(dog["id"], dog["photos"][0], test_db=True)
    delete_dog_photo(dog["id"], dog["photos"][1], test_db=True)

    # Delete dog from database
    delete_dog_by_name("Prueba")


def test_upload_cat_photos(login_org):
    # Create an object of type UploadFile to be able to upload it
    file1 = UploadFile(
        filename="image.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    file2 = UploadFile(
        filename="image2.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    post_cat(cat, test_db=True)

    upload_cat_photos(cat.id, [file1, file2], test_db=True)
    cat = get_cat_by_id(cat.id, test_db=True)
    assert len(cat["photos"]) == 2

    # Let's delete the photos from the database
    delete_cat_photo(cat["id"], cat["photos"][0], test_db=True)
    delete_cat_photo(cat["id"], cat["photos"][1], test_db=True)

    # Delete cat from database
    delete_cat_by_name("Prueba")


def test_delete_dog_photo(login_org):
    # Create an object of type UploadFile to be able to upload it
    file1 = UploadFile(
        filename="image.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    file2 = UploadFile(
        filename="image2.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    post_dog(dog, test_db=True)
    upload_dog_photos(dog.id, [file1, file2], test_db=True)
    dog = get_dog_by_id(dog.id, test_db=True)
    assert len(dog["photos"]) == 2

    # Let's delete the photos from the database
    delete_dog_photo(dog["id"], dog["photos"][0], test_db=True)
    delete_dog_photo(dog["id"], dog["photos"][1], test_db=True)

    dog = get_dog_by_id(dog["id"], test_db=True)
    assert dog["photos"] == []

    # Delete dog from database
    delete_dog_by_name("Prueba")


def test_delete_cat_photo(login_org):
    # Create an object of type UploadFile to be able to upload it
    file1 = UploadFile(
        filename="image.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    file2 = UploadFile(
        filename="image2.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    post_cat(cat, test_db=True)

    upload_cat_photos(cat.id, [file1, file2], test_db=True)
    cat = get_cat_by_id(cat.id, test_db=True)
    assert len(cat["photos"]) == 2

    # Let's delete the photos from the database
    delete_cat_photo(cat["id"], cat["photos"][0], test_db=True)
    delete_cat_photo(cat["id"], cat["photos"][1], test_db=True)

    cat = get_cat_by_id(cat["id"], test_db=True)
    assert cat["photos"] == []

    # Delete cat from database
    delete_cat_by_name("Prueba")


def test_delete_dog_by_id(login_org):
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    post_dog(dog, test_db=True)
    delete_dog_by_id(dog.id, test_db=True)
    with pytest.raises(HTTPException):
        get_dog_by_id(dog.id, test_db=True)


def test_delete_cat_by_id(login_org):
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    post_cat(cat, test_db=True)
    delete_cat_by_id(cat.id, test_db=True)
    with pytest.raises(HTTPException):
        get_cat_by_id(cat.id, test_db=True)
