from app.config.database import db
from fastapi import APIRouter, HTTPException

from app.schemas.organization import Organization

router = APIRouter()


# Create a new organization
@router.post("", status_code=201, response_model=Organization)
async def post_organization(organization: Organization):
    if db.collection("organizations").where("name", "==", organization.name).get():
        raise HTTPException(status_code=401, detail="Organization already exists")
    db.collection("organizations").document(organization.name).set(organization.dict())
    return organization
