import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from app.routes import prueba
from fastapi import FastAPI

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blueprints registration
app.include_router(prueba.router, prefix="/pruebas", tags=["Probando"])

if __name__ == "__main__":
    uvicorn.run("main:app")
