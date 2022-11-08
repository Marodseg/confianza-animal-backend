import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from app.routes import organizations, auth, animals, users, petitions, filters
from fastapi import FastAPI

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blueprints registration
app.include_router(
    organizations.router, prefix="/organizations", tags=["Organizations"]
)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(animals.router, prefix="/animals", tags=["Animals"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(petitions.router, prefix="/petitions", tags=["Petitions"])
app.include_router(filters.router, prefix="/filters", tags=["Filters"])

if __name__ == "__main__":
    uvicorn.run("main:app")
