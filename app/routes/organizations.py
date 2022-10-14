from app.config.database import db, firebase_admin_auth, pyrebase_auth
from fastapi import APIRouter, HTTPException

from app.schemas.organization import Organization, OrganizationCreate
from app.utils import hash_password

router = APIRouter()


# Register an organization
@router.post("/register", status_code=200, response_model=OrganizationCreate)
async def register_organization(organization: Organization):
    same_name = db.collection("organizations").where("name", "==", organization.name).get()
    same_phone = db.collection("organizations").where("phone", "==", organization.phone).get()
    same_email = db.collection("organizations").where("email", "==", organization.email).get()
    if same_name:
        raise HTTPException(status_code=401, detail="Organization name already exists")
    if same_phone:
        raise HTTPException(status_code=401, detail="Phone already exists")
    if same_email:
        raise HTTPException(status_code=401, detail="Email already exists")

    # It doesn't need to be in try/except as we are already checking if the email exists
    org = pyrebase_auth.create_user_with_email_and_password(organization.email, organization.password)

    # Send email verification
    try:
        pyrebase_auth.send_email_verification(org["idToken"])
        # Create organization in cloud firestore hashing password
        organization.password = hash_password(organization.password)
        db.collection("organizations").document(organization.name).set(organization.dict())
        return organization
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/login", status_code=200)
async def login_organization(email: str, password: str):
    try:
        pyrebase_auth.sign_in_with_email_and_password(email, password)
        organization = firebase_admin_auth.get_user_by_email(email)
        if organization.email_verified:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Email not verified")
    except Exception as e:
        if str(e) == "":
            raise HTTPException(status_code=401, detail="Email not verified")
        raise HTTPException(status_code=401, detail="Invalid credentials")


# Reset password endpoint
@router.post("/reset-password", status_code=200)
async def reset_password(email: str):
    try:
        pyrebase_auth.send_password_reset_email(email)
        return {"message": "Email sent to " + email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
