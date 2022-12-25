from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from pydantic import ValidationError
from requests import HTTPError

from app.config.database import test_pyrebase_auth, db_test
from app.routes.animals import get_cat_by_id, get_dog_by_id
from app.routes.organizations import (
    register_organization,
    post_cat,
    post_dog,
    get_user_profile,
    get_dogs_from_organization,
    get_cats_from_organization,
    get_organizations,
    get_organization_by_name,
    upload_profile_photo_organization,
    modify_cat,
    modify_dog,
    enable_organization,
    delete_organization,
    update_organization,
)
from app.schemas.animal import Cat, Dog, CatUpdate, DogUpdate
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.schemas.organization import Organization, OrganizationUpdateIn
from app.tests.conftest import (
    delete_organization_by_name,
    delete_cat_by_name,
    delete_dog_by_name,
)


def test_organization_register():
    # Short password (less than 6 characters)
    org = {
        "name": "testing",
        "email": "test@test.com",
        "password": "test",
        "phone": "+34123456789",
        "zone": Province.alava,
    }
    with pytest.raises(
        ValidationError, match="Password must have 6 characters at least"
    ):
        Organization(**org)

    # Invalid email (missing @)
    org = {
        "name": "testing",
        "email": "test",
        "password": "testtest",
        "phone": "+34123456789",
        "zone": Province.alava,
    }
    with pytest.raises(ValidationError, match="Email is not valid"):
        Organization(**org)

    # Invalid phone (missing +34)
    org = {
        "name": "testing",
        "email": "test@test.com",
        "password": "123456",
        "phone": "123456789",
        "zone": Province.alava,
    }
    with pytest.raises(ValidationError, match="Invalid phone number"):
        Organization(**org)

    # Valid data
    org = (
        {
            "name": "testing",
            "email": "test@test.com",
            "password": "123456",
            "phone": "+34123456789",
            "zone": Province.alava,
        },
    )
    org_created = register_organization(Organization(**org[0]), test_db=True)

    assert org_created.name == "testing"
    assert org_created.email == "test@test.com"

    # Create an organization that already exists raises an error
    with pytest.raises(HTTPException):
        register_organization(Organization(**org[0]), test_db=True)

    delete_organization_by_name("testing")


def test_login_organization(login_org):
    # Invalid password
    with pytest.raises(HTTPError, match="INVALID_PASSWORD"):
        test_pyrebase_auth.sign_in_with_email_and_password(
            "confianzaanimaltest@gmail.com", "123457"
        )

    # Invalid email
    with pytest.raises(HTTPError, match="INVALID_EMAIL"):
        test_pyrebase_auth.sign_in_with_email_and_password("jnarear", "123456")

    # Valid data
    org = test_pyrebase_auth.sign_in_with_email_and_password(
        "confianzaanimaltest@gmail.com", "123456"
    )
    assert org["email"] == "confianzaanimaltest@gmail.com"
    assert org["registered"] is True


def test_post_cat(login_org):
    # Cat with a missing fields
    with pytest.raises(ValidationError, match="field required"):
        cat = Cat(
            name="Prueba",
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

    response = post_cat(cat, test_db=True)
    assert response.name == "Prueba"
    assert response.age == 1

    # Delete cat from database
    delete_cat_by_name("Prueba")


def test_post_dog(login_org):
    # Dog with a missing fields
    with pytest.raises(ValidationError, match="field required"):
        dog = Dog(
            name="Prueba",
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

    response = post_dog(dog, test_db=True)
    assert response.name == "Prueba"
    assert response.age == 1

    # Delete dog from database
    delete_dog_by_name("Prueba")


def test_get_user_profile(login_org):
    org = get_user_profile(test_db=True)
    assert org.name == "TEST ORGANIZATION"
    assert org.email == "confianzaanimaltest@gmail.com"


def test_get_dogs_from_organization(login_org):
    # Without dogs in the organization
    dogs = get_dogs_from_organization(test_db=True)
    assert len(dogs) == 0

    # Insert a dog in the organization and check if it is returned
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

    dogs = get_dogs_from_organization(test_db=True)
    assert len(dogs) == 1
    assert dogs[0]["name"] == "Prueba"
    assert dogs[0]["raze"] == DogRaze.chihuahua

    # Delete dog from database
    delete_dog_by_name("Prueba")


def test_get_cats_from_organization(login_org):
    # Without cats in the organization
    cats = get_cats_from_organization(test_db=True)
    assert len(cats) == 0

    # Insert a dog in the organization and check if it is returned
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

    cats = get_cats_from_organization(test_db=True)
    assert len(cats) == 1
    assert cats[0]["name"] == "Prueba"
    assert cats[0]["raze"] == CatRaze.persa

    # Delete dog from database
    delete_cat_by_name("Prueba")


def test_get_organizations():
    organizations = get_organizations(test_db=True)
    assert len(organizations) == 1
    assert organizations[0].name == "TEST ORGANIZATION"


def test_get_organization_by_name():
    # With an organization that does not exist
    with pytest.raises(HTTPException):
        get_organization_by_name("TEST ORGANIZATION 2", test_db=True)

    # With an organization that exists
    org = get_organization_by_name("TEST ORGANIZATION", test_db=True)
    assert org.name == "TEST ORGANIZATION"
    assert org.email == "confianzaanimaltest@gmail.com"


def test_upload_profile_photo_organization(login_org):
    # Create an object of type UploadFile to be able to upload it
    file = UploadFile(
        filename="image.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )

    upload_profile_photo_organization(file=file, test_db=True)

    # Check if the photo is uploaded
    org = get_user_profile(test_db=True)
    assert (
        org.photo
        == "https://firebasestorage.googleapis.com/v0/b/confianza-animal-test.appspot.com/o/organizations%2FTEST%20ORGANIZATION%2Fprofile_photo?alt=media"
    )

    # Upload a photo that is not an image
    file = UploadFile(
        filename="image.txt",
        file=BytesIO(b"file_content"),
        content_type="text/plain",
    )

    with pytest.raises(HTTPException):
        upload_profile_photo_organization(file=file, test_db=True)


def test_modify_cat(login_org):
    # First, we need to have a cat in the database
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

    response = post_cat(cat, test_db=True)
    assert response.name == "Prueba"
    assert response.age == 1

    cat_id = response.id

    # Modify the cat
    new_cat = CatUpdate(
        name="Prueba 2",
    )

    modify_cat(cat_id=cat_id, new_cat=new_cat, test_db=True)

    # Check if the cat has been modified
    cat = get_cat_by_id(cat_id=cat_id, test_db=True)
    assert cat["name"] == "Prueba 2"

    # Delete the cat from the database
    delete_cat_by_name("Prueba 2")


def test_modify_dog(login_org):
    # First, we need to have a dog in the database
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

    response = post_dog(dog, test_db=True)
    assert response.name == "Prueba"
    assert response.age == 1

    dog_id = response.id

    # Modify the dog
    new_dog = DogUpdate(
        name="Prueba 2",
    )

    modify_dog(dog_id=dog_id, new_dog=new_dog, test_db=True)

    # Check if the cat has been modified
    dog = get_dog_by_id(dog_id=dog_id, test_db=True)
    assert dog["name"] == "Prueba 2"

    # Delete the cat from the database
    delete_dog_by_name("Prueba 2")


def test_enable_organization(login_org):
    # First, we force the organization to be disabled
    delete_organization(test_db=True)
    org = get_user_profile(test_db=True)
    assert org.active is False

    # Enable the organization
    enable_organization(test_db=True)
    org = get_user_profile(test_db=True)
    assert org.active is True


def test_delete_organization(login_org):
    org = get_user_profile(test_db=True)
    if org.active:
        delete_organization(test_db=True)

    # Check if the organization has been disabled
    org = get_user_profile(test_db=True)
    assert org.active is False

    # Reset the organization to active
    enable_organization(test_db=True)


def test_update_organization(login_org):
    # Assert that the zone and phone has changed:
    org = (
        db_test.collection("organizations")
        .where("name", "==", "TEST ORGANIZATION")
        .get()[0]
        .to_dict()
    )
    assert org["zone"] == Province.granada
    assert org["phone"] == "+34111111111"

    new_org = OrganizationUpdateIn(zone=Province.alava, phone="+34111111112")
    update_organization(org_update=new_org, test_db=True)
    assert new_org.zone == Province.alava
    assert new_org.phone == "+34111111112"

    # Reset the name and phone
    db_test.collection("organizations").where("name", "==", "TEST ORGANIZATION").get()[
        0
    ].reference.update({"zone": Province.granada, "phone": "+34111111111"})
    org = (
        db_test.collection("organizations")
        .where("name", "==", "TEST ORGANIZATION")
        .get()[0]
        .to_dict()
    )
    assert org["zone"] == Province.granada
    assert org["phone"] == "+34111111111"
