import datetime
from typing import List, Optional

from starlette.responses import JSONResponse

from app.config.database import db, db_test
from fastapi import APIRouter, HTTPException, Depends

from app.routes.auth import firebase_email_authentication, firebase_uid_authentication
from app.schemas.animal import AnimalsInDB
from app.schemas.enums.petition_status import PetitionStatus
from app.schemas.petition import Petition
from app.utils import exists_dog_in_animals, exists_cat_in_animals, generate_uuid

router = APIRouter()


# Create a petition for a dog
@router.post("/dog/{dog_id}", status_code=200, response_model=Petition)
def ask_for_dog(
    dog_id: str,
    message: Optional[str],
    home_type: str,
    free_time: str,
    previous_experience: str,
    frequency_travel: str,
    kids: str,
    other_animals: str,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email

    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    animals = AnimalsInDB(
        **db_a.collection("animals").document("animals").get().to_dict()
    )
    dogs = animals.dogs
    dog = next((dog for dog in dogs if dog.id == dog_id), None)

    if dog:
        petitions = (
            db_a.collection("petitions").where("user_id", "==", user["id"]).get()
        )

        for petition in petitions:
            petition = Petition(**petition.to_dict())
            if petition.dog:
                if petition.dog.id == dog_id:
                    raise HTTPException(
                        status_code=400,
                        detail="You already have a petition for this dog",
                    )
        try:
            if exists_dog_in_animals(dog_id, test_db):
                petition = Petition(
                    id=generate_uuid(),
                    user_id=user["id"],
                    user_name=user["name"],
                    user_email=user["email"],
                    dog=dog,
                    date=datetime.datetime.now(),
                    user_message=message,
                    organization_name=dog.organization_name,
                    home_type=home_type,
                    free_time=free_time,
                    previous_experience=previous_experience,
                    frequency_travel=frequency_travel,
                    kids=kids,
                    other_animals=other_animals,
                )
                db_a.collection("petitions").document(petition.id).set(
                    petition.dict(), merge=True
                )
                return petition
        except HTTPException:
            raise HTTPException(status_code=400, detail="Error creating petition")
    else:
        raise HTTPException(status_code=404, detail="Dog not found")


# Create a petition for a cat
@router.post("/cat/{cat_id}", status_code=200, response_model=Petition)
def ask_for_cat(
    cat_id: str,
    message: Optional[str],
    home_type: str,
    free_time: str,
    previous_experience: str,
    frequency_travel: str,
    kids: str,
    other_animals: str,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    animals = AnimalsInDB(
        **db_a.collection("animals").document("animals").get().to_dict()
    )
    cats = animals.cats
    cat = next((cat for cat in cats if cat.id == cat_id), None)

    if cat:
        petitions = (
            db_a.collection("petitions").where("user_id", "==", user["id"]).get()
        )
        for petition in petitions:
            petition = Petition(**petition.to_dict())
            if petition.cat:
                if petition.cat.id == cat_id:
                    raise HTTPException(
                        status_code=400,
                        detail="You already have a petition for this cat",
                    )
        try:
            if exists_cat_in_animals(cat_id, test_db):
                petition = Petition(
                    id=generate_uuid(),
                    user_id=user["id"],
                    user_name=user["name"],
                    user_email=user["email"],
                    cat=cat,
                    date=datetime.datetime.now(),
                    user_message=message,
                    organization_name=cat.organization_name,
                    home_type=home_type,
                    free_time=free_time,
                    previous_experience=previous_experience,
                    frequency_travel=frequency_travel,
                    kids=kids,
                    other_animals=other_animals,
                )
                db_a.collection("petitions").document(petition.id).set(
                    petition.dict(), merge=True
                )
                return petition
        except HTTPException:
            raise HTTPException(status_code=400, detail="Error creating petition")
    else:
        raise HTTPException(status_code=404, detail="Cat not found")


# Get petitions by user logged
@router.get("/user", status_code=200, response_model=List[Petition])
def get_petitions_by_user(
    email: str = Depends(firebase_email_authentication), test_db: bool = False
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    petitions = db_a.collection("petitions").where("user_id", "==", user["id"]).get()
    if not petitions:
        return []

    return [Petition(**petition.to_dict()) for petition in petitions]


# Get petition by id of user logged
@router.get("{petition_id}/user", status_code=200, response_model=Petition)
def get_petition_by_id_by_user(
    petition_id: str,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for petition in (
        db_a.collection("petitions").where("user_id", "==", user["id"]).get()
    ):
        petition = Petition(**petition.to_dict())
        if petition.id == petition_id:
            return petition

    raise HTTPException(status_code=404, detail="Petition not found")


# Get petitions visibles by user
@router.get("/user/visibles", status_code=200, response_model=List[Petition])
def get_petitions_visibles_by_user(
    email: str = Depends(firebase_email_authentication), test_db: bool = False
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    petitions = db_a.collection("petitions").where("user_id", "==", user["id"]).get()
    if not petitions:
        return []

    return [
        Petition(**petition.to_dict())
        for petition in petitions
        if petition.to_dict()["visible"] is True
    ]


# Get petitions invisibles by user
@router.get("/user/invisibles", status_code=200, response_model=List[Petition])
def get_petitions_invisibles_by_user(
    email: str = Depends(firebase_email_authentication), test_db: bool = False
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    petitions = db_a.collection("petitions").where("user_id", "==", user["id"]).get()
    if not petitions:
        return []

    return [
        Petition(**petition.to_dict())
        for petition in petitions
        if petition.to_dict()["visible"] is False
    ]


# Get petition from organization logged
@router.get("/organization", status_code=200, response_model=List[Petition])
def get_petitions_by_organization(
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations")
            .document("TEST ORGANIZATION")
            .get()
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    org = db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    petitions = (
        db_a.collection("petitions").where("organization_name", "==", org["name"]).get()
    )

    if not petitions:
        return []

    return [Petition(**petition.to_dict()) for petition in petitions]


# Update state of petition by organization
@router.post("/organization/{petition_id}", status_code=200, response_model=Petition)
def update_state_petition_by_organization(
    petition_id: str,
    message: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations")
            .document("TEST ORGANIZATION")
            .get()
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    org = db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    petition = (
        db_a.collection("petitions").where("id", "==", petition_id).get()[0].to_dict()
    )
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    if petition["organization_name"] != org["name"]:
        raise HTTPException(status_code=400, detail="You can't update this petition")

    if petition["status"] == PetitionStatus.initiated:
        petition["status"] = PetitionStatus.info_pending
        petition["organization_message"] = message
        db_a.collection("petitions").document(petition_id).set(petition)
        return petition

    if petition["status"] == PetitionStatus.info_pending:
        petition["status"] = PetitionStatus.info_approved
        petition["organization_message"] = message
        db_a.collection("petitions").document(petition_id).set(petition)
        return petition

    if petition["status"] == PetitionStatus.docu_envied:
        petition["status"] = PetitionStatus.docu_pending
        petition["organization_message"] = message
        db_a.collection("petitions").document(petition_id).set(petition)
        return petition

    if petition["status"] == PetitionStatus.docu_pending:
        petition["status"] = PetitionStatus.accepted
        petition["organization_message"] = message
        db_a.collection("petitions").document(petition_id).set(petition)
        return petition

    if petition["status"] == PetitionStatus.info_changed:
        petition["status"] = PetitionStatus.info_pending
        petition["organization_message"] = message
        petition["info_updated"] = False
        db_a.collection("petitions").document(petition_id).set(petition)
        return petition

    if petition["status"] == PetitionStatus.docu_changed:
        petition["status"] = PetitionStatus.docu_pending
        petition["organization_message"] = message
        petition["docu_updated"] = False
        db_a.collection("petitions").document(petition_id).set(petition)
        return petition

    return HTTPException(status_code=400, detail="Petition can't be updated")


# Reject a petition for the user documentation by organization
@router.post("/{petition_id}/organization/documentation", status_code=200)
def reject_documentation_by_organization(
    petition_id: str,
    message: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations")
            .document("TEST ORGANIZATION")
            .get()
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    org = db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    petition = db_a.collection("petitions").document(petition_id).get().to_dict()

    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    if petition["status"] == PetitionStatus.docu_pending:
        db_a.collection("petitions").document(petition_id).update(
            {"status": PetitionStatus.docu_rejected, "organization_message": message}
        )
        return JSONResponse(
            status_code=200, content={"message": "Documentation rejected"}
        )

    raise HTTPException(
        status_code=404, detail="Petition can not be rejected by documentation"
    )


# Reject a petition for the user information by organization
@router.post("/{petition_id}/organization/information", status_code=200)
def reject_information_by_organization(
    petition_id: str,
    message: str,
    home_type_bool: bool,
    free_time_bool: bool,
    previous_experience_bool: bool,
    frequency_travel_bool: bool,
    kids_bool: bool,
    other_animals_bool: bool,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations")
            .document("TEST ORGANIZATION")
            .get()
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    org = db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    petition = db_a.collection("petitions").document(petition_id).get().to_dict()

    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    if petition["status"] == PetitionStatus.docu_pending:
        db_a.collection("petitions").document(petition_id).update(
            {
                "status": PetitionStatus.info_rejected,
                "home_type_bool": home_type_bool,
                "free_time_bool": free_time_bool,
                "previous_experience_bool": previous_experience_bool,
                "frequency_travel_bool": frequency_travel_bool,
                "kids_bool": kids_bool,
                "other_animals_bool": other_animals_bool,
                "organization_message": message,
            }
        )
        return JSONResponse(
            status_code=200, content={"message": "Information rejected"}
        )

    return HTTPException(
        status_code=404, detail="Petition can not be rejected by information"
    )


# Accept a petition by id by organization
@router.post("/{petition_id}/organization", status_code=200)
def accept_petition_by_organization(
    petition_id: str,
    message: str,
    home_type_bool: bool,
    free_time_bool: bool,
    previous_experience_bool: bool,
    frequency_travel_bool: bool,
    kids_bool: bool,
    other_animals_bool: bool,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations")
            .document("TEST ORGANIZATION")
            .get()
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    org = db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    petition = db_a.collection("petitions").document(petition_id).get().to_dict()

    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    if petition["organization_name"] != org["name"]:
        raise HTTPException(
            status_code=404,
            detail="The organization is not the owner of the animal",
        )
    if (
        home_type_bool is True
        and free_time_bool is True
        and previous_experience_bool is True
        and frequency_travel_bool is True
        and kids_bool is True
        and other_animals_bool is True
    ):
        db_a.collection("petitions").document(petition_id).update(
            {"status": PetitionStatus.accepted, "organization_message": message}
        )
        return JSONResponse(status_code=200, content={"message": "Petition accepted"})

    raise HTTPException(status_code=404, detail="Petition can not be accepted")


# Switch visibility of a petition by id by user
@router.post("/{petition_id}/user", status_code=200)
def change_petition_visibility_by_user(
    petition_id: str,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    petitions = db_a.collection("petitions").where("user_id", "==", user["id"]).get()

    if not petitions:
        raise HTTPException(
            status_code=404, detail="There are no petitions for this user"
        )

    for petition in petitions:
        if petition.id == petition_id:

            if petition.to_dict()["user_id"] != user["id"]:
                raise HTTPException(
                    status_code=404, detail="The user is not the owner of the petition"
                )

            # update the status of the petition
            if petition.to_dict()["visible"] is True:
                db_a.collection("petitions").document(petition_id).update(
                    {"visible": False}
                )
            else:
                db_a.collection("petitions").document(petition_id).update(
                    {"visible": True}
                )
            return JSONResponse(
                status_code=200, content={"message": "Petition visibility changed"}
            )

    raise HTTPException(status_code=404, detail="Petition not found")


# Reject a petition by id by user
@router.delete("/{petition_id}/user", status_code=200)
def reject_petition_by_user(
    petition_id: str,
    message: str,
    email: str = Depends(firebase_email_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        email_a = (
            db_a.collection("users")
            .where("name", "==", "TEST USER")
            .get()[0]
            .to_dict()["email"]
        )
    else:
        db_a = db
        email_a = email
    user = db_a.collection("users").where("email", "==", email_a).get()[0].to_dict()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    petitions = db_a.collection("petitions").where("user_id", "==", user["id"]).get()

    if not petitions:
        raise HTTPException(
            status_code=404, detail="There are no petitions for this user"
        )

    for petition in petitions:
        if petition.id == petition_id:

            if petition.to_dict()["user_id"] != user["id"]:
                raise HTTPException(
                    status_code=404, detail="The user is not the owner of the petition"
                )

            # update the status of the petition
            db_a.collection("petitions").document(petition_id).update(
                {"status": PetitionStatus.rejected, "user_message": message}
            )
            return JSONResponse(
                status_code=200, content={"message": "Petition rejected"}
            )

    raise HTTPException(status_code=404, detail="Petition not found")


# Reject a petition by id by organization
@router.delete("/{petition_id}/organization", status_code=200)
def reject_petition_by_organization(
    petition_id: str,
    message: str,
    uid: str = Depends(firebase_uid_authentication),
    test_db: bool = False,
):
    if test_db is True:
        db_a = db_test
        uid_a = (
            db_a.collection("organizations")
            .document("TEST ORGANIZATION")
            .get()
            .to_dict()["id"]
        )
    else:
        db_a = db
        uid_a = uid
    org = db_a.collection("organizations").where("id", "==", uid_a).get()[0].to_dict()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    petition = db_a.collection("petitions").document(petition_id).get().to_dict()

    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    if petition["organization_name"] != org["name"]:
        raise HTTPException(
            status_code=404,
            detail="The organization is not the owner of the animal",
        )

    db_a.collection("petitions").document(petition_id).update(
        {"status": PetitionStatus.rejected, "organization_message": message}
    )
    return JSONResponse(status_code=200, content={"message": "Petition rejected"})
