from starlette.responses import JSONResponse

from app.config.database import db, auth, auth2
from fastapi import APIRouter, HTTPException, Request

from app.schemas.organization import Organization, OrganizationCreate

router = APIRouter()


# Create an organization
@router.post("", status_code=201, response_model=OrganizationCreate)
async def register_organization(organization: Organization):
    if db.collection("organizations").where("name", "==", organization.name).get():
        raise HTTPException(status_code=401, detail="Organization already exists")
    try:
        auth.create_user(
            email=organization.email,
            email_verified=False,
            password=organization.password,
            phone_number=organization.phone,
            display_name=organization.name,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    # send email veritifcation
    user = auth.get_user_by_email(organization.email)
    auth2.send_email_verification(user.uid)


    # link = auth.generate_email_verification_link(organization.email, action_code_settings=None)
    # send_custom_email(organization.email, link)
    db.collection("organizations").document(organization.name).set(organization.dict())
    return organization


@router.post("/login", status_code=200)
async def login_organization(request: Request):
    data = await request.json()
    organization = db.collection("organizations").where("name", "==", data["name"]).get()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if organization[0].to_dict()["password"] != data["password"]:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return JSONResponse({"message": "Logged in successfully"})
