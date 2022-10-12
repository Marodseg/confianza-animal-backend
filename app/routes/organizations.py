from app.config.database import db
from fastapi import APIRouter, HTTPException

from app.schemas.organization import Organization, OrganizationCreate

router = APIRouter()


# Create an organization
@router.post("", status_code=201, response_model=OrganizationCreate)
async def post_organization(organization: Organization):
    if db.collection("organizations").where("name", "==", organization.name).get():
        raise HTTPException(status_code=401, detail="Organization already exists")
    db.collection("organizations").document(organization.name).set(organization.dict())
    return organization
