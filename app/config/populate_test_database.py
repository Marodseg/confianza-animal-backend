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
# Execute this file to register the organization and populate the database with test data
from app.schemas.user import User


def populate_db():
    org = Organization(
        name="TEST ORGANIZATION",
        email="confianzaanimaltest@gmail.com",
        password="12345678!Ll",
        phone="+34111111111",
        zone=Province.granada,
    )
    register_organization(org, test_db=True)
    org_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "confianzaanimaltest@gmail.com", "12345678!Ll"
    )
    org.id = org_firebase["localId"]
    db_test.collection("organizations").document(org.name).update({"id": org.id})

    user = User(
        name="TEST USER",
        email="userconfianzaanimaltest@gmail.com",
        password="12345678!Ll",
        favorites={"dogs": [], "cats": []},
    )
    register_user(user, test_db=True)
    user_firebase = test_pyrebase_auth.sign_in_with_email_and_password(
        "userconfianzaanimaltest@gmail.com", "12345678!Ll"
    )
    user.id = user_firebase["localId"]
    db_test.collection("users").where("email", "==", user.email).get()[
        0
    ].reference.update({"id": user.id})


# After executing this file, you will have a test organization and a test user in the database.
if __name__ == "__main__":
    populate_db()
