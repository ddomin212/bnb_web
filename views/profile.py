""" This module contains the view functions for the profile page. """
from firebase_admin import auth
from flask import Blueprint, redirect, render_template, request, session

from utils.add import user_data
from utils.firebase import firebase_query, get_avg_ratings, get_ratings_user

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
    data = user_data(user)
    with firebase_query("posts", [("user_uid", "==", uid)]) as docs:
        docs = get_avg_ratings(docs)
        reviews, avg_rating = get_ratings_user(uid)
        return render_template(
            "profile.html",
            user=data,
            reviews=reviews,
            docs=docs,
            avg_rating=avg_rating,
        )
