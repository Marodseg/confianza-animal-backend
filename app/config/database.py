import firebase_admin
from firebase_admin import firestore, auth
import pyrebase
from app.config.firebase_config import firebase_config

# CLOUD FIRESTORE CONFIGURATION

# Make sure you have configured your env variable GOOGLE_APPLICATION_CREDENTIALS
# Linux o macOS: export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"
# Windows: $env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\username\Downloads\service-account-file.json"
firebase = firebase_admin.initialize_app()
db = firestore.client()
firebase_admin_auth = auth

# REALTIME DATABASE CONFIGURATION
realtime_firebase = pyrebase.initialize_app(firebase_config)
realtime_db = realtime_firebase.database()
pyrebase_auth = realtime_firebase.auth()
