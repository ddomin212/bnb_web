""" This module contains the routes for adding and deleting favorites. """
from flask import Blueprint, session
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from utils.firebase import update_favorites, add_favorite, firebase_get
from config import fetch_db
from utils.auth import login_required

fav = Blueprint("fav", __name__)


@fav.route("/fav/add/<pid>", methods=["GET"])
@login_required
def add_fav(pid):
    """
    Add a pid to the user's favorites. This will add the pid to the user's favorites
    if it doesn't exist and will return a 400 if it does

    @param pid - The pid to add to the user's favorites

    @return 200 if the add or update was successful, 400 if it already exists
    """
    with firebase_get("fav", session["user"]["uid"]) as fav_doc:
        if fav_doc:
            # This method is used to check if the pid is in fav_doc
            if pid in fav_doc["favs"]:
                return "Bad request", 400
            data = {"favs": fav_doc["favs"] + [pid], "timestamp": SERVER_TIMESTAMP}
            update_favorites(data)
            return "Success", 200
        else:
            data = {"favs": [pid], "timestamp": SERVER_TIMESTAMP}
            add_favorite(data)
            return "Success", 200


@fav.route("/fav/delete/<pid>", methods=["GET"])
@login_required
def delete_fav(pid):
    """
    Delete a favorite from the user's favorites.

    @param pid - The pid of the favorite to delete

    @return Either a 404 if the favorite was not found or a 200 if it was deleted.
    """
    with firebase_get("fav", session["user"]["uid"]) as fav_doc:
        found = False
        # Remove the pid from the fav_doc.
        for idx, elmnt in enumerate(fav_doc["favs"]):
            # Remove the fav from the doc.
            if elmnt == str(pid):
                fav_doc["favs"].pop(idx)
                found = True
                break
        # Return 404 if favorite not found
        if found is False:
            return "Favorite not found", 404
        data = {"favs": fav_doc["favs"], "timestamp": SERVER_TIMESTAMP}
        update_favorites(data)
        return "Success", 200
