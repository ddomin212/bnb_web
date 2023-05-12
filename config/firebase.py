import firebase_admin
from firebase_admin import firestore, credentials


def initialize_firebase():
    cred = credentials.Certificate("./config/creds.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'bnb-ai.appspot.com'
    })


def fetch_db():
    return firestore.client()
