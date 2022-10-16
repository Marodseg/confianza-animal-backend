import os

import firebase_admin
from firebase_admin import firestore, auth, credentials
import pyrebase
from app.config.firebase_config import firebase_config

# CLOUD FIRESTORE CONFIGURATION

# Make sure you have configured your env variable GOOGLE_APPLICATION_CREDENTIALS
# Linux o macOS: export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"
# Windows: $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\username\Downloads\service-account-file.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)

db = firestore.client()
firebase_admin_auth = auth

# REALTIME DATABASE CONFIGURATION
realtime_firebase = pyrebase.initialize_app(firebase_config)
realtime_db = realtime_firebase.database()
pyrebase_auth = realtime_firebase.auth()
