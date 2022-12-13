import pytest

from app.config.database import db_test
from app.routes.organizations import post_dog, post_cat
from app.routes.petitions import (
    ask_for_dog,
    ask_for_cat,
    get_petitions_by_user,
    get_petitions_by_organization,
    reject_petition_by_user,
    reject_petition_by_organization,
    accept_petition_by_organization,
    change_petition_visibility_by_user,
)
from app.schemas.animal import Dog, Cat
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.tests.conftest import delete_dog_by_name, delete_cat_by_name


def test_ask_for_dog(login_user):
    # First, let's add a dog in the database in a organization to ask for
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    ask_for_dog(dog.id, "I want this dog", test_db=True)

    # Let's check that the petition has been added to the database
    petition = (
        db_test.collection("petitions")
        .where("user_name", "==", "TEST USER")
        .get()[0]
        .to_dict()
    )
    assert petition["dog"]["id"] == dog.id
    assert petition["user_name"] == "TEST USER"
    assert petition["message"] == "I want this dog"
    assert petition["status"] == "pending"

    # If we try to ask for the same dog again, it should raise an exception
    with pytest.raises(Exception):
        ask_for_dog(dog.id, "I want this dog again", test_db=True)

    # Let's delete the dog and the petition from the database
    db_test.collection("petitions").document(petition["id"]).delete()
    delete_dog_by_name("Prueba")


def test_ask_for_cat(login_user):
    # First, let's add a cat in the database in a organization to ask for
    cat = Cat(
        name="Prueba",
        age=1,
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

    cat = post_cat(cat, test_db=True)
    ask_for_cat(cat.id, "I want this cat", test_db=True)

    # Let's check that the petition has been added to the database
    petition = (
        db_test.collection("petitions")
        .where("user_name", "==", "TEST USER")
        .get()[0]
        .to_dict()
    )
    assert petition["cat"]["id"] == cat.id
    assert petition["user_name"] == "TEST USER"
    assert petition["message"] == "I want this cat"
    assert petition["status"] == "pending"

    # If we try to ask for the same cat again, it should raise an exception
    with pytest.raises(Exception):
        ask_for_cat(cat.id, "I want this cat again", test_db=True)

    # Let's delete the cat and the petition from the database
    db_test.collection("petitions").document(petition["id"]).delete()
    delete_cat_by_name("Prueba")


def test_get_petitions_by_user(login_user):
    # Let's create two petitions (e.g. asking for a dog and for a cat)
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    petition1 = ask_for_dog(dog.id, "I want this dog", test_db=True)

    cat = Cat(
        name="Prueba",
        age=1,
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

    cat = post_cat(cat, test_db=True)
    petition2 = ask_for_cat(cat.id, "I want this cat", test_db=True)

    petitions = get_petitions_by_user(test_db=True)
    # Order the petitions, first the dog and then the cat

    # Let's check that the petitions are the same as the ones we created
    assert len(petitions) == 2
    if petitions[0].dog is None:
        petitions.reverse()
    assert petitions[0].dog.id == dog.id
    assert petitions[1].cat.id == cat.id
    assert petitions[0].user_name == "TEST USER"
    assert petitions[1].user_name == "TEST USER"
    assert petitions[0].message == "I want this dog"
    assert petitions[1].message == "I want this cat"

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition1.id).delete()
    db_test.collection("petitions").document(petition2.id).delete()
    delete_dog_by_name("Prueba")
    delete_cat_by_name("Prueba")


def test_get_petitions_by_organization(login_user, login_org):
    # Let's create two petitions (e.g. asking for a dog and for a cat)
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    petition1 = ask_for_dog(dog.id, "I want this dog", test_db=True)

    cat = Cat(
        name="Prueba",
        age=1,
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

    cat = post_cat(cat, test_db=True)
    petition2 = ask_for_cat(cat.id, "I want this cat", test_db=True)

    petitions = get_petitions_by_organization(test_db=True)
    # Order the petitions, first the dog and then the cat

    # Let's check that the petitions are the same as the ones we created
    assert len(petitions) == 2
    if petitions[0].dog is None:
        petitions.reverse()
    assert petitions[0].dog.id == dog.id
    assert petitions[1].cat.id == cat.id
    assert petitions[0].user_name == "TEST USER"
    assert petitions[1].user_name == "TEST USER"
    assert petitions[0].message == "I want this dog"
    assert petitions[1].message == "I want this cat"
    assert petitions[0].organization_name == "TEST ORGANIZATION"
    assert petitions[1].organization_name == "TEST ORGANIZATION"

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition1.id).delete()
    db_test.collection("petitions").document(petition2.id).delete()
    delete_dog_by_name("Prueba")
    delete_cat_by_name("Prueba")


def test_reject_petition_by_user(login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(dog.id, "I want this dog", test_db=True)

    # Check that the petition is pending when is created
    assert petition.status == "pending"

    reject_petition_by_user(petition.id, test_db=True)

    # Check that the petition is rejected
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == "rejected"
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_reject_petition_by_organization(login_org):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(dog.id, "I want this dog", test_db=True)

    # Check that the petition is pending when is created
    assert petition.status == "pending"

    reject_petition_by_organization(petition.id, test_db=True)

    # Check that the petition is rejected
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == "rejected"
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_accept_petition_by_organization(login_org):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(dog.id, "I want this dog", test_db=True)

    # Check that the petition is pending when is created
    assert petition.status == "pending"

    accept_petition_by_organization(petition.id, test_db=True)

    # Check that the petition is accepted
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == "approved"
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_change_petition_visibility_by_user(login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        age=1,
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

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(dog.id, "I want this dog", test_db=True)

    # Check that the petition is visible when is created
    assert petition.visible is True

    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that the petition is not visible
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["visible"]
        is False
    )

    # Change again the visibility to turn in True
    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that the petition visibility is True
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["visible"]
        is True
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")
