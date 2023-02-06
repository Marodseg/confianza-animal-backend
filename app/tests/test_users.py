from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from pydantic import ValidationError
from requests import HTTPError

from app.config.database import test_pyrebase_auth, db_test
from app.routes.organizations import post_dog
from app.routes.petitions import (
    ask_for_dog,
    update_state_petition_by_organization,
    accept_information_by_organization,
    reject_documentation_by_organization,
)
from app.routes.users import (
    register_user,
    get_user_profile,
    get_user_by_id,
    disable_user,
    enable_user,
    upload_profile_photo,
    update_user,
    update_user_documentation,
    envy_user_documentation,
    post_user_favorites,
    get_user_favorites,
    check_if_animal_is_in_favorites,
    delete_favorite,
)
from app.schemas.animal import Dog
from app.schemas.enums.activity import Activity
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.petition_status import PetitionStatus
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.schemas.user import User, UserUpdateIn
from app.tests.conftest import delete_user_by_name, delete_dog_by_name


def test_user_register():
    # Short password (less than 8 characters)
    with pytest.raises(
        ValidationError,
        match="Password must have 8 characters and contain at least one number, one uppercase and one symbol",
    ):
        User(
            name="testing",
            email="test@test.com",
            password="12345",
            favorites={"dogs": [], "cats": []},
        )

    # Invalid email (missing @)
    with pytest.raises(ValidationError, match="Email is not valid"):
        User(
            name="testing",
            email="testtest.com",
            password="12345678!Ll",
            favorites={"dogs": [], "cats": []},
        )

    # Valid data
    user = User(
        name="testing",
        email="test@test.com",
        password="12345678!Ll",
        favorites={"dogs": [], "cats": []},
    )
    user_created = register_user(user, test_db=True)

    assert user_created.name == "testing"
    assert user_created.email == "test@test.com"

    # Create an organization that already exists raises an error
    with pytest.raises(HTTPException):
        register_user(user, test_db=True)

    delete_user_by_name("testing")


def test_login_user(login_user):
    # Invalid password
    with pytest.raises(HTTPError, match="INVALID_PASSWORD"):
        test_pyrebase_auth.sign_in_with_email_and_password(
            "userconfianzaanimaltest@gmail.com", "1234578!La"
        )

    # Invalid email
    with pytest.raises(HTTPError, match="INVALID_EMAIL"):
        test_pyrebase_auth.sign_in_with_email_and_password("jnarear", "12345678!Ll")

    # Valid data
    org = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "12345678!Ll"
    )
    assert org["email"] == "userconfianzaanimaltest@gmail.com"
    assert org["registered"] is True


def test_get_user_profile(login_user):
    user = get_user_profile(test_db=True)
    assert user.name == "TEST USER"
    assert user.email == "userconfianzaanimaltest@gmail.com"


def test_get_user_favorites(login_user):
    # Let's create a dog favorite
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

    dog = post_dog(dog, test_db=True)

    # Mark it as favorite
    post_user_favorites(dog.id, test_db=True)
    # Get favorites
    favorites = get_user_favorites(test_db=True)

    assert favorites == {"dogs": [dog], "cats": []}

    # Delete favorites and animals from the database
    db_test.collection("users").where("name", "==", "TEST USER").get()[
        0
    ].reference.update({"favorites": {"dogs": [], "cats": []}})
    delete_dog_by_name("Prueba")


def test_check_if_animal_is_in_favorites(login_user):
    # Let's create a dog favorite
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

    dog = post_dog(dog, test_db=True)

    # Mark it as favorite
    post_user_favorites(dog.id, test_db=True)
    # Check if the dog is in the favorites
    assert check_if_animal_is_in_favorites(dog.id, test_db=True) is True

    # Delete favorites and animals from the database
    db_test.collection("users").where("name", "==", "TEST USER").get()[
        0
    ].reference.update({"favorites": {"dogs": [], "cats": []}})
    delete_dog_by_name("Prueba")


def test_get_user_by_id(login_user):
    with pytest.raises(HTTPException):
        get_user_by_id("invalid_id", test_db=True)

    user_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "12345678!Ll"
    )
    user = get_user_by_id(user_firebase["localId"], test_db=True)
    assert user["name"] == "TEST USER"
    assert user["email"] == "userconfianzaanimaltest@gmail.com"


def test_envy_user_documentation(login_user, login_org):
    # Let's create a petition
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

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.initiated
    )

    # To reject the information we need to change the state to "info_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_pending
    )
    # Accept the information to pass to docu_pending
    accept_information_by_organization(
        petition.id,
        "Actualizo estado",
        True,
        True,
        True,
        True,
        True,
        True,
        test_db=True,
    )
    # Check that the status is in info_approved
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_approved
    )
    # Now we need the user to send the information and update the state to "docu_envied"
    envy_user_documentation(petition.id, "Doc enviada", test_db=True)
    # Check that the status is in docu_envied
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_envied
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_post_user_favorites(login_user):
    # Let's create a petition
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

    dog = post_dog(dog, test_db=True)

    # Mark it as favorite
    post_user_favorites(dog.id, test_db=True)
    # Check that the dog is in the favorites
    assert db_test.collection("users").where("name", "==", "TEST USER").get()[
        0
    ].to_dict()["favorites"]["dogs"] == [dog]

    # Delete favorites and animals from the database
    db_test.collection("users").where("name", "==", "TEST USER").get()[
        0
    ].reference.update({"favorites": {"dogs": [], "cats": []}})
    delete_dog_by_name("Prueba")


def test_enable_user(login_user):
    # First, we force the user to be disabled
    disable_user(test_db=True)
    org = get_user_profile(test_db=True)
    assert org.active is False

    # Enable the user
    enable_user(test_db=True)
    org = get_user_profile(test_db=True)
    assert org.active is True


def test_disable_user(login_user):
    org = get_user_profile(test_db=True)
    if org.active:
        disable_user(test_db=True)

    # Check if the user has been disabled
    org = get_user_profile(test_db=True)
    assert org.active is False

    # Reset the user to active
    enable_user(test_db=True)


def test_upload_profile_photo(login_user):
    # Create an object of type UploadFile to be able to upload it
    file = UploadFile(
        filename="image.jpg",
        file=BytesIO(b"file_content"),
        content_type="image/jpeg",
    )

    upload_profile_photo(file=file, test_db=True)

    # Check if the photo is uploaded
    user = get_user_profile(test_db=True)
    assert (
        user.photo
        == "https://firebasestorage.googleapis.com/v0/b/confianza-animal-test.appspot.com/o/users%2F"
        + user.id
        + "%2Fprofile_photo?alt=media"
    )

    # Upload a photo that is not an image
    file = UploadFile(
        filename="image.txt",
        file=BytesIO(b"file_content"),
        content_type="text/plain",
    )

    with pytest.raises(HTTPException):
        upload_profile_photo(file=file, test_db=True)


def test_update_user(login_user):
    # Assert that the name has changed:
    user = (
        db_test.collection("users").where("name", "==", "TEST USER").get()[0].to_dict()
    )
    assert user["name"] == "TEST USER"

    new_user = UserUpdateIn(name="TEST USER UPDATED")
    update_user(user=new_user, test_db=True)
    assert new_user.name == "TEST USER UPDATED"

    # Reset the name
    db_test.collection("users").where("name", "==", "TEST USER UPDATED").get()[
        0
    ].reference.update({"name": "TEST USER"})
    user = (
        db_test.collection("users").where("name", "==", "TEST USER").get()[0].to_dict()
    )
    assert user["name"] == "TEST USER"


def test_update_user_documentation(login_user, login_org):
    # Let's create a petition
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

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )
    update_user_documentation(petition.id, "La actualizo", test_db=True)
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_pending
    )
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["user_message"]
        == "La actualizo"
    )
    # If the documentation is rejected and the user updates it, the status changes to docu_changed
    reject_documentation_by_organization(petition.id, "Falta el DNI", test_db=True)
    update_user_documentation(petition.id, "Te paso el DNI", test_db=True)
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_changed
    )
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["user_message"]
        == "Te paso el DNI"
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_delete_favorite(login_user):
    # Let's create a dog favorite
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

    dog = post_dog(dog, test_db=True)

    # Mark it as favorite
    post_user_favorites(dog.id, test_db=True)
    # Get favorites
    favorites = get_user_favorites(test_db=True)

    assert favorites == {"dogs": [dog], "cats": []}

    # Delete the favorite
    delete_favorite(dog.id, test_db=True)

    assert get_user_favorites(test_db=True) == {"dogs": [], "cats": []}
    delete_dog_by_name("Prueba")
