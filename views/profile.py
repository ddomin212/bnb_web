""" This module contains the view functions for the profile page. """
from flask import Blueprint, render_template, redirect, request, session
from firebase_admin import auth
from config import fetch_db
from utils.firebase import get_avg_rating, get_ratings_user

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


@profile.route("/user/<uid>", methods=["GET"])
def view_user(uid):
    """
    View a user's posts. This is a view function that returns a the user's page.

    @param uid - The user's id. This is the id of the user who is viewing the posts.

    @return An HTML page that contains the user's profile, with posts, ratings.
            Optionally the user can have a description and a phone number.
    """
    user = auth.get_user(uid)
    try:
        desc = user.custom_claims["description"]
    except Exception:
        desc = ""

    try:
        phone = user.custom_claims["phone"]
    except Exception:
        phone = ""
    data = {
        "displayName": user.display_name,
        "email": user.email,
        "description": desc,
        "uid": user.uid,
        "photoURL": user.photo_url,
        "phoneNumber": phone,
    }
    history = fetch_db().collection("posts").where("user_uid", "==", uid).stream()
    docs = [doc.to_dict() for doc in history]
    # Get the average rating of all the docs in the document
    for doc in docs:
        print(doc)
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    reviews = get_ratings_user(uid)
    ratings = [review["rating"] for review in reviews]
    avg_rating = sum(ratings) / len(ratings) if len(ratings) > 0 else 0
    return render_template(
        "profile.html", user=data, reviews=reviews, docs=docs, avg_rating=avg_rating
    )
