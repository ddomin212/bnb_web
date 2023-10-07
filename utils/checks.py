from flask import session

from components.firebase.database import firebase_query
from utils.render import render_message


def check_self(pid: int) -> None:
    """
    Check if a user is reviewing their own property.
    """
    with firebase_query("posts", [("id", "==", int(pid))]) as data:
        doc = data[0]
        # If the user is the user s uid
        if doc["user_uid"] == session["user"]["uid"]:
            return False
    return True


def check_duplicate(pid: int) -> None:
    """
    Check if a user has already reviewed a property.
    """
    with firebase_query(
        "reviews",
        [
            ("reviewed", "==", int(pid)),
            ("reviewer", "==", session["user"]["uid"]),
        ],
    ) as data:
        if len(data) > 0:
            return False
    return True
