import os

from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
}

test_firebase_config = {
    "apiKey": os.getenv("TEST_FIREBASE_API_KEY"),
    "authDomain": os.getenv("TEST_FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("TEST_FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("TEST_FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("TEST_FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("TEST_FIREBASE_APP_ID"),
    "measurementId": os.getenv("TEST_FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.getenv("TEST_FIREBASE_DATABASE_URL"),
}
