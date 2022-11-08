from typing import List

from fastapi.security import OAuth2PasswordRequestForm
from google.cloud.firestore_v1 import ArrayUnion, DELETE_FIELD, ArrayRemove
from starlette.responses import JSONResponse

from app.config.database import db, firebase_admin_auth, pyrebase_auth, storage
from fastapi import APIRouter, HTTPException, Depends, UploadFile

from app.routes.auth import (
    firebase_email_authentication,
    Token,
    firebase_uid_authentication,
)
from app.schemas.animal import Dog, Cat, DogUpdate, CatUpdate
from app.schemas.organization import (
    Organization,
    OrganizationCreate,
    OrganizationAnimals,
    OrganizationUpdateIn,
    OrganizationUpdateOut,
)
from app.utils import (
    exists_email_in_organization,
    exists_name_in_organization,
    exists_phone_in_organization,
    generate_uuid,
)

router = APIRouter()


# Get organization with token
@router.get("/me", status_code=200, response_model=OrganizationAnimals)
async def get_user_profile(uid: str = Depends(firebase_uid_authentication)):
    org = db.collection("organizations").where("id", "==", uid).get()
    if org:
        return OrganizationAnimals(**org[0].to_dict())
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


# Get all organizations
@router.get("/", status_code=200, response_model=List[OrganizationCreate])
async def get_organizations():
    organizations = db.collection("organizations").get()
    return [OrganizationCreate(**org.to_dict()) for org in organizations]


# Get organization by name
@router.get("/{organization_name}", status_code=200, response_model=OrganizationAnimals)
async def get_organization_by_name(organization_name: str):
    organization = (
        db.collection("organizations")
        .where("name", "==", organization_name)
        .where("active", "==", True)
        .get()
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationAnimals(**organization[0].to_dict())


# Post a dog to an organization
@router.post("/dog", status_code=200, response_model=Dog)
async def post_dog(
    dog: Dog,
    uid: str = Depends(firebase_uid_authentication),
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    dog.id = generate_uuid()
    dog.organization_name = org["name"]
    dog.organization_phone = org["phone"]
    dog.organization_photo = org["photo"]

    db.collection("organizations").document(org["name"]).update(
        {"dogs": ArrayUnion([dog.dict()])}
    )
    db.collection("animals").document("animals").set(
        {"dogs": ArrayUnion([dog.dict()])}, merge=True
    )
    return dog


# Post a cat to an organization
@router.post("/cat", status_code=200, response_model=Cat)
async def post_cat(
    cat: Cat,
    uid: str = Depends(firebase_uid_authentication),
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    cat.id = generate_uuid()
    cat.organization_name = org["name"]
    cat.organization_phone = org["phone"]
    cat.organization_photo = org["photo"]

    db.collection("organizations").document(org["name"]).update(
        {"cats": ArrayUnion([cat.dict()])}
    )
    db.collection("animals").document("animals").set(
        {"cats": ArrayUnion([cat.dict()])}, merge=True
    )
    return cat


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
        organization.id = org["localId"]
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


@router.post("/login", status_code=200, response_model=Token)
async def login_organization(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        org = pyrebase_auth.sign_in_with_email_and_password(
            form_data.username, form_data.password
        )
        organization = firebase_admin_auth.get_user_by_email(form_data.username)

        # Search an organization by email in the database
        my_org = (
            db.collection("organizations")
            .where("email", "==", form_data.username)
            .get()[0]
            .to_dict()
        )

        if organization.email_verified:
            if not exists_email_in_organization(form_data.username):
                return JSONResponse(
                    status_code=403, content={"message": "You are not an organization"}
                )
            if not my_org["active"]:
                return JSONResponse(
                    status_code=401,
                    content={"message": "This organization is inactive"},
                )
            return JSONResponse(status_code=200, content={"token": org["idToken"]})
        else:
            raise HTTPException(status_code=401, detail="Email not verified")
    except Exception as e:
        if str(e) == "":
            raise HTTPException(status_code=401, detail="Email not verified")
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Upload photo profile
@router.post("/upload/photo", status_code=200)
async def upload_profile_photo_organization(
    file: UploadFile, email: str = Depends(firebase_email_authentication)
):
    org = db.collection("organizations").where("email", "==", email).get()[0].to_dict()

    try:
        # Upload a photo to Firebase Storage ensuring that the file is an image
        if file.content_type.startswith("image/"):
            # Get the file extension
            extension = file.filename.split(".")[-1]

            # Generate a random name for the file
            filename = "profile_photo"  # Here we can add the extension
            # But we want to overwrite the previous photo

            # Upload the file and delete the previous one
            storage.child(f"organizations/{org['name']}/{filename}").put(file.file)
            # Get the url of the uploaded file
            url = storage.child(f"organizations/{org['name']}/{filename}").get_url(None)
            # Update the user's photo
            db.collection("organizations").document(org["name"]).update({"photo": url})
            return JSONResponse(status_code=200, content={"message": "Photo uploaded"})
        else:
            raise HTTPException(status_code=401, detail="File is not an image")
    except Exception as e:
        raise HTTPException(status_code=401, detail="File is not an image")


# Modify a dog from an organization
@router.put("/dog/{dog_id}", status_code=200, response_model=Dog)
async def modify_dog(
    dog_id: str,
    new_dog: DogUpdate,
    uid: str = Depends(firebase_uid_authentication),
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    dogs = db.collection("organizations").document(org["name"]).get().to_dict()["dogs"]

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
            db.collection("organizations").document(org["name"]).update(
                {"dogs": ArrayRemove([old_dog])}
            )
            db.collection("organizations").document(org["name"]).update(
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


# Modify a cat from an organization
@router.put("/cat/{cat_id}", status_code=200, response_model=Cat)
async def modify_cat(
    cat_id: str,
    new_cat: CatUpdate,
    uid: str = Depends(firebase_uid_authentication),
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    cats = db.collection("organizations").document(org["name"]).get().to_dict()["cats"]

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
            db.collection("organizations").document(org["name"]).update(
                {"cats": ArrayRemove([old_cat])}
            )
            db.collection("organizations").document(org["name"]).update(
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


# Enable organization
@router.put("/enable", status_code=200)
async def enable_organization(uid: str = Depends(firebase_uid_authentication)):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if org["active"]:
        raise HTTPException(status_code=400, detail="Organization already enabled")

    db.collection("organizations").document(org["name"]).update({"active": True})
    return JSONResponse(status_code=200, content={"message": "Organization enabled"})


# Update organization
@router.put("/update", status_code=200, response_model=OrganizationUpdateOut)
async def update_organization(
    org_update: OrganizationUpdateIn, uid: str = Depends(firebase_uid_authentication)
):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if the changes exists in the database
    if org_update.phone:
        if db.collection("organizations").where("phone", "==", org_update.phone).get():
            raise HTTPException(status_code=409, detail="Phone already exists")

    if org_update.name:
        if db.collection("organizations").where("name", "==", org_update.name).get():
            raise HTTPException(status_code=409, detail="Name already exists")

    # We keep a copy of the old organization
    old_org = org.copy()

    if org_update.name:
        old_org["name"] = org_update.name
    if org_update.phone:
        old_org["phone"] = org_update.phone
    if org_update.zone:
        old_org["zone"] = org_update.zone

    try:
        db.collection("organizations").document(old_org["name"]).update(old_org)
        new_org = (
            db.collection("organizations").document(old_org["name"]).get().to_dict()
        )
        return new_org
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# delete organization
@router.delete("/disable", status_code=200)
async def delete_organization(uid: str = Depends(firebase_uid_authentication)):
    org = db.collection("organizations").where("id", "==", uid).get()[0].to_dict()

    if not org["active"]:
        raise HTTPException(status_code=401, detail="Organization already disabled")

    db.collection("organizations").document(org["name"]).update({"active": False})
    return JSONResponse(status_code=200, content={"message": "Organization disabled"})
