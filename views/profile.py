""" This module contains the view functions for the profile page. """
from flask import Blueprint, render_template, redirect, request, session
from google.cloud.exceptions import GoogleCloudError
from firebase_admin import auth
from utils.firebase import get_avg_ratings, get_ratings_user
from utils.firebase import firebase_query

profile = Blueprint("profile", __name__)


@profile.route("/user/add-info", methods=["POST"])
def add_description():
    """
    Add a description to the user's claims. This is used to add a
    description to the user that can be show on their profile page.
    """
    phone = request.form["phone"]
    description = request.form["description"]
    data = {"phone": phone, "description": description[:1000]}
    auth.set_custom_user_claims(session["user"]["uid"], data)
    return redirect("/user/" + session["user"]["uid"])


@profile.route("/user/<string:uid>", methods=["GET"])
def view_user(uid: str):
    """
    View a user's posts. This is a view function that returns a the user's page.

    @param uid - The user's id. This is the id of the user who is viewing the posts.

    @return An HTML page that contains the user's profile, with posts, ratings.
            Optionally the user can have a description and a phone number.
    """
    user = auth.get_user(uid)
    try:
        desc = user.custom_claims["description"]
        phone = user.custom_claims["phone"]
    except GoogleCloudError:
        desc = ""
        phone = ""

    data = {
        "displayName": user.display_name,
        "email": user.email,
        "description": desc,
        "uid": user.uid,
        "photoURL": user.photo_url,
        "phoneNumber": phone,
    }
    with firebase_query("posts", [("user_uid", "==", uid)]) as docs:
        docs = get_avg_ratings(docs)
        reviews, avg_rating = get_ratings_user(uid)
        return render_template(
            "profile.html", user=data, reviews=reviews, docs=docs, avg_rating=avg_rating
        )
