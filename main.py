import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from app.routes import organizations, auth, animals, users, petitions, filters
from fastapi import FastAPI

description = """
**Confianza Animal API** helps you do to manage a database of animals, organizations and users.

This API is part of the **Confianza Animal project**:

* A **web application** that helps an organization to manage a database of animals 
* An **android application** that helps users to find a pet to adopt.

## Authentication (for users and organizations)

You can:

* **Reset** your password.

## Organizations

You can:

* **Create** an organization.
* **Login** in the the web application.
* **Get** your own information.
* **Update** your organization.
* **Disable/Enable** your organization.
* **Get** all the organizations.
* **Get** a specific organization by name.
* **Upload** a photo of your organization.
* **Upload/Update** an animal **(dog or cat)** in your organization.
* **Get** all the animals of your organization.
* **Update** an animal of your organization.

## Users

You can:

* **Create** a user.
* **Login** in the the android application.
* **Get** your own information.
* **Update** your user.
* **Disable/Enable** your user.
* **Update** your user's photo.
* **Get** all the animals requested by your user.
* **Envy** documentation for a petition
* **Update** the documentation for a petition.
* **Mark** an animal as favorite.
* **Get** all the animals marked as favorite by your user.

## Animals (managed by organizations)

You can:

* **Get** all the animals.
* **Get** a specific animal **(dog/cat)** by id.
* **Get** all the animals with filters:
    * **Size**.
        * **Mini**.
        * **Small**.
        * **Medium**.
        * **Big**.
        * **Very big**.
    * **Years:** with the parameter ***greater_or_equal*** allows you to choose if the age of the animal must be ≥ or ≤ than the number specified in the years field.
    * **Gender**.
        * **Male**.
        * **Female**.
    * **Raze (Chihuahua, bulldog, dalmata, ..., or other)**.
    * **Activity**.
        * **Low**.
        * **Medium**.
        * **High**.
    * **Urgency:** specify if the adoption of the animal is urgent or not.
    * **Zone:** specify the province where the animal is located (Albacete, Alicante, ...).
* **Upload/Delete photos of specific animals by id**.

## Petitions (managed by users and organizations)

You can:

* **Create** a petition for a specific animal **(dog/cat)** by id.
* **Get** all the petitions of your organization.
* **Get** all the petitions of your user.
* **Delete** a petition of your organization by id.
* **Delete** a petition of your user by id.
* **Update** the status of a petition by organization.
* **Reject** a petition by user or organization.
* **Accept** a petition by user or organization.
* **Accept** or **Reject** the information or documentation of a petition by organization.
* **Change** the visibility of a petition by user (visible/invisible).
* **Get** all the petitions visibles/inivisibles by user.

## Filters

You can:

* **Get** all the filters.
* **Get** the filters by zone/province.
* **Get** the filters by gender.
* **Get** the filters by size.
* **Get** the filters by dog raze.
* **Get** the filters by cat raze.
"""

app = FastAPI(
    title="Confianza Animal",
    description=description,
    version="0.0.1",
    contact={
        "name": "Manuel Ángel Rodríguez Segura",
        "url": "http://linkedin.com/in/marodseg",
        "email": "manuelangelrodriguezsegura@gmail.com",
    },
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
    "https://confianza-animal.web.app",
    "https://ca-frontend.web.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blueprints registration
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(
    organizations.router, prefix="/organizations", tags=["Organizations"]
)
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(animals.router, prefix="/animals", tags=["Animals"])
app.include_router(petitions.router, prefix="/petitions", tags=["Petitions"])
app.include_router(filters.router, prefix="/filters", tags=["Filters"])

if __name__ == "__main__":
    uvicorn.run("main:app")
