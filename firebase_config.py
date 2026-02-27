import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
}

# Initialize Pyrebase for auth
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize Firebase Admin for Firestore
if os.path.exists("firebase_key.json"):
    cred = credentials.Certificate("firebase_key.json")
else:
    # Use environment variable for Streamlit Cloud secrets
    firebase_secret = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if firebase_secret:
        # Load the dict directly from the JSON string
        cred_dict = json.loads(firebase_secret)
        cred = credentials.Certificate(cred_dict)
    else:
        raise ValueError("Firebase credentials not found! Ensure FIREBASE_SERVICE_ACCOUNT is set in your Cloud Secrets.")

try:
    firebase_admin.get_app()  # Check if already initialized
except ValueError:
    firebase_admin.initialize_app(cred)
db = firestore.client()