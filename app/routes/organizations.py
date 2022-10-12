from app.config.database import db
from fastapi import APIRouter

from app.schemas.animal import Animal
from app.schemas.organization import Organization

router = APIRouter()


@router.post("/organization", status_code=201, response_model=Organization)
async def post_organization(organization: Organization):
    # CHECK HERE IF THE NAME ALREADY EXISTS IN THE DATABASE
    # IF IT EXISTS, RETURN A 400 BAD REQUEST
    # IF IT DOESN'T EXIST, CREATE THE ORGANIZATION
    db.collection("organizations").document(organization.name).set(organization.dict())
    return organization


@router.post("/organization/{organization_name}/animal", status_code=201)
async def post_animal(organization_name: str, animal: Animal):
    # get organization by name
    organization = (
        db.collection("organizations").where("name", "==", organization_name).get()
    )
    # add animal in the animals of the organization
    organization[0].reference.update(
        {"animals": organization[0].to_dict()["animals"] + [animal]}
    )
    return {"message": "Animal created successfully"}
