import os

from dotenv import load_dotenv

import firebase_admin

from firebase_admin import firestore, auth, credentials

import pyrebase

from app.config.firebase_config import firebase_config, test_firebase_config

load_dotenv()

# CLOUD FIRESTORE CONFIGURATION

# Make sure you have configured your env variable GOOGLE_APPLICATION_CREDENTIALS // TEST
# Linux o macOS: export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"
# Windows: $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\username\Downloads\service-account-file.json"
cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
cred_test = credentials.Certificate(
    os.environ.get("TEST_GOOGLE_APPLICATION_CREDENTIALS")
)

default_app = firebase_admin.initialize_app(cred)
test_app = firebase_admin.initialize_app(cred_test, name="test")

# General database
db = firestore.client(default_app)
# Database used exclusively for testing
db_test = firestore.client(test_app)

# AUTHENTICATION CONFIGURATION
firebase_admin_auth = auth

# REALTIME DATABASE CONFIGURATION
realtime_firebase = pyrebase.initialize_app(firebase_config)
realtime_db = realtime_firebase.database()
pyrebase_auth = realtime_firebase.auth()

# REALTIME DATABASE CONFIGURATION FOR TESTING
test_realtime_firebase = pyrebase.initialize_app(test_firebase_config)
test_realtime_db = test_realtime_firebase.database()
test_pyrebase_auth = test_realtime_firebase.auth()

# STORAGE
storage = realtime_firebase.storage()

# STORAGE FOR TESTING
test_storage = test_realtime_firebase.storage()
