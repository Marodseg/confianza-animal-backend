from app.config.database import db


def exists_email_in_organization(email: str) -> bool:
    return db.collection("organizations").where("email", "==", email).get()


def exists_phone_in_organization(phone: str) -> bool:
    return db.collection("organizations").where("phone", "==", phone).get()


def exists_name_in_organization(name: str) -> bool:
    return db.collection("organizations").where("name", "==", name).get()
