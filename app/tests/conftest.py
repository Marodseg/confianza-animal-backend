import pytest

from app.config.database import db_test, test_pyrebase_auth


def delete_organization_by_name(name: str):
    org = (
        db_test.collection("organizations").where("name", "==", name).get()[0].to_dict()
    )
    user = test_pyrebase_auth.sign_in_with_email_and_password(org["email"], "123456")
    db_test.collection("organizations").document(org["name"]).delete()
    test_pyrebase_auth.delete_user_account(user["idToken"])


def delete_user_by_name(name: str):
    user = db_test.collection("users").where("name", "==", name).get()[0].to_dict()
    user_db = test_pyrebase_auth.sign_in_with_email_and_password(
        user["email"], "123456"
    )
    db_test.collection("users").document(user["id"]).delete()
    test_pyrebase_auth.delete_user_account(user_db["idToken"])


def delete_cat_by_name(name: str):
    # Get cat array from animals
    cats = db_test.collection("animals").document("animals").get().to_dict()["cats"]
    # Delete cat from array
    for cat in cats:
        if cat["name"] == name:
            cats.remove(cat)
    # Update animals document
    db_test.collection("animals").document("animals").update({"cats": cats})
    # Delete cat from organization
    db_test.collection("organizations").document("TEST ORGANIZATION").update(
        {"cats": cats}
    )


def delete_dog_by_name(name: str):
    # Get dog array from animals
    dogs = db_test.collection("animals").document("animals").get().to_dict()["dogs"]
    # Delete dog from array
    for dog in dogs:
        if dog["name"] == name:
            dogs.remove(dog)
    # Update animals document
    db_test.collection("animals").document("animals").update({"dogs": dogs})
    # Delete cat from organization
    db_test.collection("organizations").document("TEST ORGANIZATION").update(
        {"dogs": dogs}
    )


@pytest.fixture
def login_org() -> str:
    org = test_pyrebase_auth.sign_in_with_email_and_password(
        "confianzaanimaltest@gmail.com", "123456"
    )
    if org:
        return org["idToken"]
    else:
        raise Exception("Error logging in")


@pytest.fixture
def login_user() -> str:
    user = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "123456"
    )
    if user:
        return user["idToken"]
    else:
        raise Exception("Error logging in")
