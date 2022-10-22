from google.cloud.firestore_v1 import ArrayUnion, DELETE_FIELD, ArrayRemove
from starlette.responses import JSONResponse

from app.config.database import db, firebase_admin_auth, pyrebase_auth
from fastapi import APIRouter, HTTPException, Depends

from app.routes.auth import firebase_authentication
from app.schemas.animal import Dog, Cat, DogUpdate, CatUpdate
from app.schemas.organization import (
    Organization,
    OrganizationCreate,
    OrganizationAnimals,
)
from app.utils import (
    exists_email_in_organization,
    exists_name_in_organization,
    exists_phone_in_organization,
    generate_uuid,
)

router = APIRouter()


# Get all organizations
@router.get("/", status_code=200, response_model=list[OrganizationCreate])
async def get_organizations():
    organizations = db.collection("organizations").get()
    return [OrganizationCreate(**org.to_dict()) for org in organizations]


# Get organization by name
@router.get("/{org_name}", status_code=200, response_model=OrganizationAnimals)
async def get_organization_by_name(org_name: str):
    organization = db.collection("organizations").where("name", "==", org_name).get()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationAnimals(**organization[0].to_dict())


# Post a dog to an organization
@router.post("/dog/{org_name}", status_code=200, response_model=Dog)
async def post_dog(
    org_name: str, dog: Dog, email: str = Depends(firebase_authentication)
):
    if exists_name_in_organization(org_name):
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):
            # Generate a random id for the dog
            dog.id = generate_uuid()
            # Include the organization data in the dog
            dog.organization_name = org_name
            dog.organization_phone = (
                db.collection("organizations")
                .document(org_name)
                .get()
                .to_dict()["phone"]
            )
            dog.organization_photo = (
                db.collection("organizations")
                .document(org_name)
                .get()
                .to_dict()["photo"]
            )

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
@router.post("/cat/{org_name}", status_code=200, response_model=Cat)
async def post_cat(
    org_name: str, cat: Cat, email: str = Depends(firebase_authentication)
):
    if db.collection("organizations").document(org_name).get().exists:
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):
            # Generate a unique id for the cat
            cat.id = generate_uuid()
            # Include the organization data in the cat
            cat.organization_name = org_name
            cat.organization_phone = (
                db.collection("organizations")
                .document(org_name)
                .get()
                .to_dict()["phone"]
            )
            cat.organization_photo = (
                db.collection("organizations")
                .document(org_name)
                .get()
                .to_dict()["photo"]
            )
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


# Modify a dog from an organization
@router.put("/dog/{dog_id}", status_code=200, response_model=Dog)
async def modify_dog(
    org_name: str,
    dog_id: str,
    new_dog: DogUpdate,
    email: str = Depends(firebase_authentication),
):
    if exists_name_in_organization(org_name):

        # check if the email is the same as the organization email
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):

            dogs = (
                db.collection("organizations")
                .document(org_name)
                .get()
                .to_dict()["dogs"]
            )

            for (count, dog) in enumerate(dogs, start=1):
                if dog["id"] == dog_id:
                    # We keep a copy of the old dog
                    old_dog = dog.copy()

                    # We keep the same id as it was
                    new_dog.id = dog_id
                    for key, value in new_dog.dict().items():
                        if value is not None:  # Only the fields that are updated
                            dog[key] = value

                    new_dog = dog.copy()

                    # We update the dog in the organization
                    db.collection("organizations").document(org_name).update(
                        {"dogs": ArrayRemove([old_dog])}
                    )
                    db.collection("organizations").document(org_name).update(
                        {"dogs": ArrayUnion([new_dog])}
                    )
                    # We update the dog in the global animals
                    db.collection("animals").document("animals").update(
                        {"dogs": ArrayRemove([old_dog])}
                    )
                    db.collection("animals").document("animals").update(
                        {"dogs": ArrayUnion([new_dog])}
                    )
                    return new_dog
                else:
                    # In case there are no more
                    if len(dogs) == count:
                        raise HTTPException(status_code=404, detail="Dog not found")
        else:
            raise HTTPException(
                status_code=401, detail="You are not authorized to do this"
            )
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


# Modify a cat from an organization
@router.put("/cat/{cat_id}", status_code=200, response_model=Cat)
async def modify_cat(
    org_name: str,
    cat_id: str,
    new_cat: CatUpdate,
    email: str = Depends(firebase_authentication),
):
    if exists_name_in_organization(org_name):

        # check if the email is the same as the organization email
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):

            cats = (
                db.collection("organizations")
                .document(org_name)
                .get()
                .to_dict()["cats"]
            )

            for (count, cat) in enumerate(cats, start=1):
                if cat["id"] == cat_id:
                    # We keep a copy of the old cat
                    old_cat = cat.copy()

                    # We keep the same id as it was
                    new_cat.id = cat_id
                    for key, value in new_cat.dict().items():
                        if value is not None:  # Only the fields that are updated
                            cat[key] = value

                    new_cat = cat.copy()

                    # We update the cat in the organization
                    db.collection("organizations").document(org_name).update(
                        {"cats": ArrayRemove([old_cat])}
                    )
                    db.collection("organizations").document(org_name).update(
                        {"cats": ArrayUnion([new_cat])}
                    )

                    # We update the cat in the global animals
                    db.collection("animals").document("animals").update(
                        {"cats": ArrayRemove([old_cat])}
                    )
                    db.collection("animals").document("animals").update(
                        {"cats": ArrayUnion([new_cat])}
                    )
                    return new_cat
                else:
                    # In case there are no more
                    if len(cats) == count:
                        raise HTTPException(status_code=404, detail="Cat not found")
        else:
            raise HTTPException(
                status_code=401, detail="You are not authorized to do this"
            )
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


# enable organization
@router.put("/enable/{org_name}", status_code=200)
async def enable_organization(
    org_name: str, email: str = Depends(firebase_authentication)
):
    if exists_name_in_organization(org_name):
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):
            db.collection("organizations").document(org_name).update({"active": True})
            return {"message": "Organization enabled"}
        else:
            raise HTTPException(
                status_code=401, detail="You are not authorized to do this"
            )
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


# delete organization
@router.delete("/delete/{org_name}", status_code=200)
async def delete_organization(
    org_name: str, email: str = Depends(firebase_authentication)
):
    if exists_name_in_organization(org_name):
        if (
            db.collection("organizations").document(org_name).get().to_dict()["email"]
            == email
        ):
            db.collection("organizations").document(org_name).update({"active": False})
            return {"message": "Organization deleted"}
        else:
            raise HTTPException(
                status_code=401, detail="You are not authorized to do this"
            )
    else:
        raise HTTPException(status_code=404, detail="Organization not found")
