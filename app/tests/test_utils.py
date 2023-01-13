from app.config.database import test_pyrebase_auth
from app.routes.organizations import post_dog, post_cat
from app.schemas.animal import Dog, Cat
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.tests.conftest import delete_dog_by_name, delete_cat_by_name
from app.utils import (
    exists_email_in_organization,
    exists_phone_in_organization,
    exists_name_in_organization,
    exists_id_in_user,
    exists_dog_in_animals,
    exists_cat_in_animals,
    get_dog_or_cat_by_filters,
    generate_uuid,
)


def test_exists_email_in_organization():
    # Find the organization with the email
    org = exists_email_in_organization("confianzaanimaltest@gmail.com", test_db=True)
    assert org is not None
    assert org[0].to_dict()["email"] == "confianzaanimaltest@gmail.com"


def test_exists_phone_in_organization():
    # Find the organization with the phone
    org = exists_phone_in_organization("+34111111111", test_db=True)
    assert org is not None
    assert org[0].to_dict()["phone"] == "+34111111111"


def test_exists_name_in_organization():
    # Find the organization with the name
    org = exists_name_in_organization("TEST ORGANIZATION", test_db=True)
    assert org is not None
    assert org[0].to_dict()["name"] == "TEST ORGANIZATION"


def test_exists_id_in_user():
    # Get user by name
    user_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "123456"
    )
    user = exists_id_in_user(user_firebase["localId"], test_db=True)
    assert user is not None
    assert user[0].to_dict()["id"] == user_firebase["localId"]


def test_exists_dog_in_animals():
    # Add a dog to the database
    dog = Dog(
        name="Prueba",
        age=1,
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
    assert exists_dog_in_animals(dog.id, test_db=True) is True

    # Delete dog from database
    delete_dog_by_name("Prueba")


def test_exists_cat_in_animals():
    # Add a cat to the database
    cat = Cat(
        name="Prueba",
        age=1,
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
    assert exists_cat_in_animals(cat.id, test_db=True) is True

    # Delete cat from database
    delete_cat_by_name("Prueba")


def test_get_dog_or_cat_by_filters():
    dog1 = {
        "name": "Dog1",
        "age": 1,
        "gender": Gender.male,
        "weight": 1.0,
        "size": Size.small,
        "zone": Province.alava,
        "neutered": True,
        "description": "Dog1",
        "healthy": True,
        "wormed": True,
        "vaccinated": True,
        "activity_level": Activity.low,
        "microchip": True,
        "is_urgent": True,
        "raze": DogRaze.chihuahua,
    }
    dog2 = {
        "name": "Dog2",
        "age": 1,
        "gender": Gender.male,
        "weight": 1.0,
        "size": Size.small,
        "zone": Province.granada,
        "neutered": True,
        "description": "Dog2",
        "healthy": True,
        "wormed": True,
        "vaccinated": True,
        "activity_level": Activity.low,
        "microchip": True,
        "is_urgent": True,
        "raze": DogRaze.akita,
    }
    cat1 = {
        "name": "Cat1",
        "age": 1,
        "gender": Gender.male,
        "weight": 1.0,
        "size": Size.small,
        "zone": Province.granada,
        "neutered": True,
        "description": "Prueba",
        "healthy": True,
        "wormed": True,
        "vaccinated": True,
        "activity_level": Activity.low,
        "microchip": True,
        "is_urgent": True,
        "raze": CatRaze.persa,
    }
    cat2 = {
        "name": "Cat2",
        "age": 1,
        "gender": Gender.female,
        "weight": 1.0,
        "size": Size.mini,
        "zone": Province.salamanca,
        "neutered": True,
        "description": "Cat2",
        "healthy": True,
        "wormed": True,
        "vaccinated": True,
        "activity_level": Activity.low,
        "microchip": True,
        "is_urgent": True,
        "raze": CatRaze.bengal,
    }
    animals = [dog1, dog2, cat1, cat2]

    filtered_animals = get_dog_or_cat_by_filters(animals, size=Size.small)
    assert len(filtered_animals) == 3
    filtered_animals = get_dog_or_cat_by_filters(
        animals, size=Size.small, province=Province.alava
    )
    assert len(filtered_animals) == 1
    assert filtered_animals[0]["name"] == "Dog1"
    filtered_animals = get_dog_or_cat_by_filters(animals, gender=Gender.female)
    assert len(filtered_animals) == 1
    assert filtered_animals[0]["name"] == "Cat2"


def test_generate_uuid():
    # Generate a uuid
    uuid = generate_uuid()
    assert uuid is not None
    assert len(uuid) == 32
