import pytest

from app.config.database import db_test
from app.routes.organizations import post_dog, post_cat
from app.routes.petitions import (
    ask_for_dog,
    ask_for_cat,
    get_petitions_by_user,
    get_petitions_by_organization,
    reject_petition_by_user,
    reject_petition_by_organization,
    accept_petition_by_organization,
    change_petition_visibility_by_user,
    get_petitions_visibles_by_user,
    get_petitions_invisibles_by_user,
    reject_information_by_organization,
    update_state_petition_by_organization,
    reject_documentation_by_organization,
    get_petition_by_id_by_user,
)
from app.routes.users import envy_user_documentation
from app.schemas.animal import Dog, Cat
from app.schemas.enums.activity import Activity
from app.schemas.enums.cat_raze import CatRaze
from app.schemas.enums.dog_raze import DogRaze
from app.schemas.enums.gender import Gender
from app.schemas.enums.petition_status import PetitionStatus
from app.schemas.enums.provinces import Province
from app.schemas.enums.size import Size
from app.tests.conftest import delete_dog_by_name, delete_cat_by_name


def test_ask_for_dog(login_user):
    # First, let's add a dog in the database in a organization to ask for
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Let's check that the petition has been added to the database
    petition = (
        db_test.collection("petitions")
        .where("user_name", "==", "TEST USER")
        .get()[0]
        .to_dict()
    )
    assert petition["dog"]["id"] == dog.id
    assert petition["user_name"] == "TEST USER"
    assert petition["user_message"] == "I want this dog"
    assert petition["home_type"] == "casa"
    assert petition["free_time"] == "2h"
    assert petition["previous_experience"] == "si"
    assert petition["frequency_travel"] == "2 veces al mes"
    assert petition["kids"] == "si"
    assert petition["other_animals"] == "si"
    assert petition["status"] == PetitionStatus.initiated

    # If we try to ask for the same dog again, it should raise an exception
    with pytest.raises(Exception):
        ask_for_dog(
            dog.id,
            "I want this dog",
            "casa",
            "2h",
            "si",
            "2 veces al mes",
            "si",
            "si",
            test_db=True,
        )

    # Let's delete the dog and the petition from the database
    db_test.collection("petitions").document(petition["id"]).delete()
    delete_dog_by_name("Prueba")


def test_ask_for_cat(login_user):
    # First, let's add a cat in the database in a organization to ask for
    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    cat = post_cat(cat, test_db=True)
    ask_for_cat(
        cat.id,
        "I want this cat",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Let's check that the petition has been added to the database
    petition = (
        db_test.collection("petitions")
        .where("user_name", "==", "TEST USER")
        .get()[0]
        .to_dict()
    )
    assert petition["cat"]["id"] == cat.id
    assert petition["user_name"] == "TEST USER"
    assert petition["user_message"] == "I want this cat"
    assert petition["home_type"] == "casa"
    assert petition["free_time"] == "2h"
    assert petition["previous_experience"] == "si"
    assert petition["frequency_travel"] == "2 veces al mes"
    assert petition["kids"] == "si"
    assert petition["other_animals"] == "si"
    assert petition["status"] == PetitionStatus.initiated

    # If we try to ask for the same cat again, it should raise an exception
    with pytest.raises(Exception):
        ask_for_cat(
            cat.id,
            "I want this cat",
            "casa",
            "2h",
            "si",
            "2 veces al mes",
            "si",
            "si",
            test_db=True,
        )

    # Let's delete the cat and the petition from the database
    db_test.collection("petitions").document(petition["id"]).delete()
    delete_cat_by_name("Prueba")


def test_get_petitions_by_user(login_user):
    # Let's create two petitions (e.g. asking for a dog and for a cat)
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition1 = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    cat = post_cat(cat, test_db=True)
    petition2 = ask_for_cat(
        cat.id,
        "I want this cat",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    petitions = get_petitions_by_user(test_db=True)
    # Order the petitions, first the dog and then the cat

    # Let's check that the petitions are the same as the ones we created
    assert len(petitions) == 2
    if petitions[0].dog is None:
        petitions.reverse()
    assert petitions[0].dog.id == dog.id
    assert petitions[1].cat.id == cat.id
    assert petitions[0].user_name == "TEST USER"
    assert petitions[1].user_name == "TEST USER"
    assert petitions[0].user_message == "I want this dog"
    assert petitions[1].user_message == "I want this cat"

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition1.id).delete()
    db_test.collection("petitions").document(petition2.id).delete()
    delete_dog_by_name("Prueba")
    delete_cat_by_name("Prueba")


def test_get_petition_by_id_by_user(login_user):
    # Let's create two petitions (e.g. asking for a dog and for a cat)
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    petition = get_petition_by_id_by_user(petition.id, test_db=True)

    # Let's check that the petitions are the same as the ones we created
    assert petition.dog.id == dog.id
    assert petition.user_name == "TEST USER"
    assert petition.user_message == "I want this dog"
    assert petition.home_type == "casa"
    assert petition.kids == "si"

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_get_petitions_by_organization(login_user, login_org):
    # Let's create two petitions (e.g. asking for a dog and for a cat)
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition1 = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    cat = Cat(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=CatRaze.persa,
    )

    cat = post_cat(cat, test_db=True)
    petition2 = ask_for_cat(
        cat.id,
        "I want this cat",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    petitions = get_petitions_by_organization(test_db=True)
    # Order the petitions, first the dog and then the cat

    # Let's check that the petitions are the same as the ones we created
    assert len(petitions) == 2
    if petitions[0].dog is None:
        petitions.reverse()
    assert petitions[0].dog.id == dog.id
    assert petitions[1].cat.id == cat.id
    assert petitions[0].user_name == "TEST USER"
    assert petitions[1].user_name == "TEST USER"
    assert petitions[0].user_message == "I want this dog"
    assert petitions[1].user_message == "I want this cat"
    assert petitions[0].organization_name == "TEST ORGANIZATION"
    assert petitions[1].organization_name == "TEST ORGANIZATION"

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition1.id).delete()
    db_test.collection("petitions").document(petition2.id).delete()
    delete_dog_by_name("Prueba")
    delete_cat_by_name("Prueba")


def test_reject_petition_by_user(login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that the petition is pending when is created
    assert petition.status == PetitionStatus.initiated

    reject_petition_by_user(petition.id, "No me interesa", test_db=True)

    # Check that the petition is rejected
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.rejected
    )
    # And the message is the one we sent
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["user_message"]
        == "No me interesa"
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_reject_petition_by_organization(login_org):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that the petition is pending when is created
    assert petition.status == PetitionStatus.initiated

    reject_petition_by_organization(petition.id, "Se ha adoptado ya", test_db=True)

    # Check that the petition is rejected
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.rejected
    )
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["organization_message"]
        == "Se ha adoptado ya"
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_accept_petition_by_organization(login_org):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that the petition is pending when is created
    assert petition.status == PetitionStatus.initiated

    accept_petition_by_organization(
        petition.id, "Aceptado", True, True, True, True, True, True, test_db=True
    )

    # Check that the petition is accepted
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.accepted
    )

    # If there is one boolean that is false, the animal can't be adopted
    with pytest.raises(Exception):
        accept_petition_by_organization(
            petition.id, "Aceptado", False, True, True, True, True, True, test_db=True
        )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_change_petition_visibility_by_user(login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that the petition is visible when is created
    assert petition.visible is True

    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that the petition is not visible
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["visible"]
        is False
    )

    # Change again the visibility to turn in True
    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that the petition visibility is True
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["visible"]
        is True
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_get_petitions_visibles_by_user(login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that the petition is visible when is created
    assert petition.visible is True

    # Check that we are getting this petition
    petitions = get_petitions_visibles_by_user(test_db=True)
    assert petitions[0].id == petition.id
    assert len(petitions) == 1

    # Change the visibility to False
    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that we are not getting this petition
    petitions = get_petitions_visibles_by_user(test_db=True)
    assert petitions == []

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_get_petitions_invisibles_by_user(login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that the petition is visible when is created
    assert petition.visible is True

    # Let's change the visibility to False
    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that we are getting this petition
    petitions = get_petitions_invisibles_by_user(test_db=True)
    assert petitions[0].id == petition.id
    assert len(petitions) == 1

    # Change the visibility to True
    change_petition_visibility_by_user(petition.id, test_db=True)

    # Check that we are not getting this petition
    petitions = get_petitions_invisibles_by_user(test_db=True)
    assert petitions == []

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_update_state_petition_by_organization(login_org, login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.initiated
    )

    # Update the state to "docu_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_pending
    )
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_approved
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_approved
    )
    # Now we need the user to send the information and update the state to "docu_envied"
    envy_user_documentation(petition.id, "Doc enviada", test_db=True)
    # Check that the status is in docu_envied
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_envied
    )
    # Update the state to "docu_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in docu_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_pending
    )
    # Update the state to "approved" and check the final status
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.accepted
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_reject_documentation_by_organization(login_org, login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.initiated
    )

    # Update the state to "docu_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_pending
    )
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_approved
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_approved
    )
    # Now we need the user to send the information and update the state to "docu_envied"
    envy_user_documentation(petition.id, "Doc enviada", test_db=True)
    # Check that the status is in docu_envied
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_envied
    )
    # Update the state to "docu_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in docu_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_pending
    )
    reject_documentation_by_organization(
        petition.id, "Rechazo la documentación", test_db=True
    )
    # Check that the status is in docu_rejected
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_rejected
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")


def test_reject_information_by_organization(login_org, login_user):
    # Let's create a petition
    dog = Dog(
        name="Prueba",
        years=1,
        gender=Gender.male,
        photos=[
            "https://www.image.com/image.jpg",
            "https://www.image.com/image2.jpg",
        ],
        weight=1.0,
        size=Size.small,
        zone=Province.alava,
        neutered=True,
        description="Prueba",
        healthy=True,
        wormed=True,
        vaccinated=True,
        activity_level=Activity.low,
        microchip=True,
        is_urgent=True,
        raze=DogRaze.chihuahua,
    )

    dog = post_dog(dog, test_db=True)
    petition = ask_for_dog(
        dog.id,
        "I want this dog",
        "casa",
        "2h",
        "si",
        "2 veces al mes",
        "si",
        "si",
        test_db=True,
    )

    # Check that if we reject the information but the status is not docu_pending, the status is not changed
    reject_information_by_organization(
        petition.id,
        "Información nula",
        True,
        True,
        False,
        True,
        True,
        True,
        test_db=True,
    )
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.initiated
    )

    # To reject the information we need to change the state to "docu_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_pending
    )
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in info_approved
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_approved
    )
    # Now we need the user to send the information and update the state to "docu_envied"
    envy_user_documentation(petition.id, "Doc enviada", test_db=True)
    # Check that the status is in docu_envied
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_envied
    )
    # Update the state to "docu_pending"
    update_state_petition_by_organization(petition.id, "Actualizo estado", test_db=True)
    # Check that the status is in docu_pending
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.docu_pending
    )
    # Now we can reject the information
    reject_information_by_organization(
        petition.id,
        "Información nula",
        True,
        True,
        False,
        True,
        True,
        True,
        test_db=True,
    )

    # Check that the information is rejected
    assert (
        db_test.collection("petitions").document(petition.id).get().to_dict()["status"]
        == PetitionStatus.info_rejected
    )
    # Check that the booleans are sent correctly
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["home_type_bool"]
        is True
    )
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["free_time_bool"]
        is True
    )
    assert (
        db_test.collection("petitions")
        .document(petition.id)
        .get()
        .to_dict()["previous_experience_bool"]
        is False
    )

    # Delete petitions and animals from the database
    db_test.collection("petitions").document(petition.id).delete()
    delete_dog_by_name("Prueba")
