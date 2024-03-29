import os

from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
}

test_firebase_config = {
    "apiKey": os.environ.get("TEST_FIREBASE_API_KEY"),
    "authDomain": os.environ.get("TEST_FIREBASE_AUTH_DOMAIN"),
    "projectId": os.environ.get("TEST_FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("TEST_FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("TEST_FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("TEST_FIREBASE_APP_ID"),
    "measurementId": os.environ.get("TEST_FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.environ.get("TEST_FIREBASE_DATABASE_URL"),
}
