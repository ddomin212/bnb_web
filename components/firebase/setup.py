""" Firebase configuration module. """
import firebase_admin
from firebase_admin import firestore, credentials

class FirebaseComponent:
    def __init__(self):
        """
        Initialize Firebase with default credentials.
        """
        cred = credentials.Certificate("./components/creds.json")
        firebase_admin.initialize_app(cred, {"storageBucket": "bnb-ai.appspot.com"})


def connect_to_firestore():
    """
    Fetch the firestore database client.


    @return A : class : ` firestore. client ` instance that can
                        be used to interact with the database
    """
    return firestore.client()
