""" Firebase configuration module. """
import firebase_admin
from firebase_admin import firestore, credentials


def initialize_firebase():
    """
    Initialize Firebase with default credentials.
    """
    cred = credentials.Certificate("./config/creds.json")
    firebase_admin.initialize_app(cred, {"storageBucket": "bnb-ai.appspot.com"})


def fetch_db():
    """
    Fetch the firestore database client.


    @return A : class : ` firestore. client ` instance that can
                        be used to interact with the database
    """
    return firestore.client()
