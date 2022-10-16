import uuid

from google.cloud.firestore_v1 import ArrayUnion, DELETE_FIELD
from starlette.responses import JSONResponse

from app.config.database import db, firebase_admin_auth, pyrebase_auth
from fastapi import APIRouter, HTTPException, Depends

from app.routes.auth import firebase_authentication
from app.schemas.animal import Dog, Cat
from app.schemas.organization import Organization, OrganizationCreate
from app.utils import (
    exists_email_in_organization,
    exists_name_in_organization,
    exists_phone_in_organization,
)

router = APIRouter()


# Get all organizations
# @router.get("/", status_code=200, response_model=list[OrganizationCreate])
# async def get_organizations():
#     organizations = db.collection("organizations").get()
#     return [OrganizationCreate(**org.to_dict()) for org in organizations]


# Register an organization
@router.post("/register", status_code=200, response_model=OrganizationCreate)
async def register_organization(organization: Organization):
    if exists_name_in_organization(organization.name):
        raise HTTPException(status_code=401, detail="Organization name already exists")
    if exists_phone_in_organization(organization.phone):
        raise HTTPException(status_code=401, detail="Phone already exists")
    if exists_email_in_organization(organization.email):
        raise HTTPException(status_code=401, detail="Email already exists")

    try:
        org = pyrebase_auth.create_user_with_email_and_password(
            organization.email, organization.password
        )
    except HTTPException:
        raise HTTPException(status_code=400, detail="Error creating user")

    try:
        db.collection("organizations").document(organization.name).set(
            organization.dict()
        )
        # For security, we don't save the password in the database
        # as is handled by Firebase Authentication
        db.collection("organizations").document(organization.name).update(
            {"password": DELETE_FIELD}
        )
        # Send email verification
        pyrebase_auth.send_email_verification(org["idToken"])
        return organization
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login", status_code=200)
async def login_organization(email: str, password: str):
    try:
        org = pyrebase_auth.sign_in_with_email_and_password(email, password)
        organization = firebase_admin_auth.get_user_by_email(email)
        if organization.email_verified:
            if not exists_email_in_organization(email):
                return JSONResponse(
                    status_code=403, content={"message": "You are not an organization"}
                )
            return JSONResponse(status_code=200, content={"token": org["idToken"]})
        else:
            raise HTTPException(status_code=401, detail="Email not verified")
    except Exception as e:
        if str(e) == "":
            raise HTTPException(status_code=401, detail="Email not verified")
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Post a dog to an organization
@router.post("/dog", status_code=200, response_model=Dog)
async def post_dog(
    org_name: str, dog: Dog, email: str = Depends(firebase_authentication)
):
    if exists_name_in_organization(org_name):
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):
            # Generate a random id for the dog
            dog.id = str(uuid.uuid4())
            db.collection("organizations").document(org_name).update(
                {"dogs": ArrayUnion([dog.dict()])}
            )
            db.collection("animals").document("animals").set(
                {"dogs": ArrayUnion([dog.dict()])}, merge=True
            )
            return dog
        else:
            raise HTTPException(
                status_code=401, detail="You are not authorized to do this"
            )
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


# Post a cat to an organization
@router.post("/cat", status_code=200, response_model=Cat)
async def post_cat(
    org_name: str, cat: Cat, email: str = Depends(firebase_authentication)
):
    if db.collection("organizations").document(org_name).get().exists:
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):
            # Generate a unique id for the cat
            cat.id = str(uuid.uuid4())
            db.collection("organizations").document(org_name).update(
                {"cats": ArrayUnion([cat.dict()])}
            )
            db.collection("animals").document("animals").set(
                {"cats": ArrayUnion([cat.dict()])}, merge=True
            )
            return cat
        else:
            raise HTTPException(
                status_code=401, detail="You are not authorized to do this"
            )
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


# Modify a dog from an organization
# @router.put("/dog", status_code=200, response_model=Dog)
# async def modify_dog(org_name: str, dog: Dog, email: str = Depends(firebase_authentication)):
#     if db.collection("organizations").document(org_name).get().exists:
#         # check if the email is the same as the organization email
#         if db.collection("organizations").document(org_name).get().to_dict()["email"] == email:
#             dogs = db.collection("organizations").document(org_name).get().to_dict()["dogs"]
#             for i in range(len(dogs)):
#                 if dogs[i]["name"] == dog.name:
#                     dogs[i] = dog.dict()
#                     db.collection("organizations").document(org_name).update({"dogs": dogs})
#                     return dog
#             raise HTTPException(status_code=404, detail="Dog not found")
#         else:
#             raise HTTPException(status_code=401, detail="You are not authorized to do this")
#     else:
#         raise HTTPException(status_code=404, detail="Organization not found")
