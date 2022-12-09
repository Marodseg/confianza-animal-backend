from app.config.database import test_pyrebase_auth, db_test
from app.routes.organizations import register_organization
from app.routes.users import register_user
from app.schemas.enums.provinces import Province
from app.schemas.organization import Organization

####################################################################################################
####################################  IMPORTANT NOTE: ##############################################
################################  FOLLOW THE STEPS BELOW:  #########################################
############################## (IS ALSO EXPLAINED IN THE README) ###################################
####################################################################################################

# FIRST STEP:
# Make sure you have configured your env variable GOOGLE_APPLICATION_CREDENTIALS // TEST
# Linux o macOS: export TEST_GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"
# Windows: $env:TEST_GOOGLE_APPLICATION_CREDENTIALS="C:\Users\username\Downloads\service-account-file.json"


# SECOND STEP:
# Execute this file to register the organization and populate the database with test data as follows:
# pytest app/config/populate_test_database.py
from app.schemas.user import User


def test_populate_db():
    org = Organization(
        name="TEST ORGANIZATION",
        email="confianzaanimaltest@gmail.com",
        password="123456",
        phone="+34111111111",
        zone=Province.granada,
    )
    register_organization(org, test_db=True)
    org_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "confianzaanimaltest@gmail.com", "123456"
    )
    org.id = org_firebase["localId"]
    db_test.collection("organizations").document(org.name).update({"id": org.id})

    user = User(
        name="TEST USER", email="userconfianzaanimaltest@gmail.com", password="123456"
    )
    register_user(user, test_db=True)
    user_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "123456"
    )
    user.id = user_firebase["localId"]
    db_test.collection("users").where("email", "==", user.email).get()[
        0
    ].reference.update({"id": user.id})


# If the test is successful, the organization will be registered and the database will be populated with test data.
# If the test fails, it is because the test database has suffered some changes and is not as the original blank database.
