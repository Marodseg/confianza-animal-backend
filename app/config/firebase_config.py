import os

from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "apiKey": os.environ["FIREBASE_API_KEY"],
    "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
    "projectId": os.environ["FIREBASE_PROJECT_ID"],
    "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": os.environ["FIREBASE_APP_ID"],
    "measurementId": os.environ["FIREBASE_MEASUREMENT_ID"],
    "databaseURL": os.environ["FIREBASE_DATABASE_URL"],
}

test_firebase_config = {
    "apiKey": os.environ["TEST_FIREBASE_API_KEY"],
    "authDomain": os.environ["TEST_FIREBASE_AUTH_DOMAIN"],
    "projectId": os.environ["TEST_FIREBASE_PROJECT_ID"],
    "storageBucket": os.environ["TEST_FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": os.environ["TEST_FIREBASE_MESSAGING_SENDER_ID"],
    "appId": os.environ["TEST_FIREBASE_APP_ID"],
    "measurementId": os.environ["TEST_FIREBASE_MEASUREMENT_ID"],
    "databaseURL": os.environ["TEST_FIREBASE_DATABASE_URL"],
}
