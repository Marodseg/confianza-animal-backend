from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from pydantic import ValidationError
from requests import HTTPError

from app.config.database import test_pyrebase_auth, db_test
from app.routes.users import (
    register_user,
    get_user_profile,
    get_user_by_id,
    disable_user,
    enable_user,
    upload_profile_photo,
    update_user,
)
from app.schemas.user import User, UserUpdateIn
from app.tests.conftest import delete_user_by_name, delete_cat_by_name


def test_organization_register():
    # Short password (less than 6 characters)
    with pytest.raises(
        ValidationError, match="Password must have 6 characters at least"
    ):
        User(name="testing", email="test@test.com", password="12345")

    # Invalid email (missing @)
    with pytest.raises(ValidationError, match="Email is not valid"):
        User(name="testing", email="testtest.com", password="123456")

    # Valid data
    user = User(
        name="testing",
        email="test@test.com",
        password="123456",
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
            "userconfianzaanimaltest@gmail.com", "123457"
        )

    # Invalid email
    with pytest.raises(HTTPError, match="INVALID_EMAIL"):
        test_pyrebase_auth.sign_in_with_email_and_password("jnarear", "123456")

    # Valid data
    org = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "123456"
    )
    assert org["email"] == "userconfianzaanimaltest@gmail.com"
    assert org["registered"] is True


def test_get_user_profile(login_user):
    user = get_user_profile(test_db=True)
    assert user.name == "TEST USER"
    assert user.email == "userconfianzaanimaltest@gmail.com"


def test_get_user_by_id(login_user):
    with pytest.raises(HTTPException):
        get_user_by_id("invalid_id", test_db=True)

    user_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "123456"
    )
    user = get_user_by_id(user_firebase["localId"], test_db=True)
    assert user["name"] == "TEST USER"
    assert user["email"] == "userconfianzaanimaltest@gmail.com"


def test_enable_user(login_user):
    # First, we force the user to be disabled
    disable_user(test_db=True)
    org = get_user_profile(test_db=True)
    assert org.active is False

    # Enable the user
    enable_user(test_db=True)
    org = get_user_profile(test_db=True)
    assert org.active is True


def test_disable_organization(login_user):
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
        == "https://firebasestorage.googleapis.com/v0/b/confianza-animal-test.appspot.com/o/users%2F1y9VWoRfhtZRjoIVdzTroacWK7F3%2Fprofile_photo?alt=media"
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
