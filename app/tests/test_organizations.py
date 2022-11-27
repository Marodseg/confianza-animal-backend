from fastapi.testclient import TestClient

from app.schemas.enums.provinces import Province
from main import app

client = TestClient(app)


def test_organization_register():
    # Short password (less than 6 characters)
    response = client.post("/organizations/register",
                           json={"name": "test", "email": "test@test.com", "password": "test", "phone": "+34123456789", "zone": Province.alava})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "password"
                ],
                "msg": "Password must have 6 characters at least",
                "type": "value_error"
            }
        ]
    }
    # Invalid email (missing @)
    response = client.post("/organizations/register",
                            json={"name": "test", "email": "test", "password": "testtest", "phone": "+34123456789", "zone": Province.alava})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "email"
                ],
                "msg": "Email is not valid",
                "type": "value_error"
            }
        ]
    }
    # Invalid phone (missing +34)
    response = client.post("/organizations/register",
                            json={"name": "test", "email": "test@test.com", "password": "123456", "phone": "123456789", "zone": Province.alava})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "phone"
                ],
                "msg": "Invalid phone number. Must be +34XXXXXXXXX",
                "type": "value_error"
            }
        ]
    }
    # Valid data
    response = client.post("/organizations/register",
                            json={"name": "test (PLEASE DO NOT DELETE)", "email": "test@test.com", "password": "123456", "phone": "+34123456789", "zone": Province.alava})
    assert response.status_code == 200


def test_organization_login():
    response = client.post("/organizations/login",
                            data={"username": "test@test.com", "password": "123456"},
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
    print (response.json())
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Email not verified"
    }

