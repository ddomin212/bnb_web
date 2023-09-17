""" This file contains the views for reviews. It allows you to add, edit and delete reviews. """
from flask import Blueprint, redirect, render_template, request, session
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

from utils.checks import check_duplicate, check_self
from utils.firebase import (
    add_to_firestore,
    firebase_get,
    firebase_query,
    update_firestore,
)
from utils.render import render_message

reviews = Blueprint("reviews", __name__)


@reviews.route("/review/add/<int:pid>", methods=["GET", "POST"])
def add_review(pid: int):
    """
    Add a review to a post. This is a POST and a GET.
    It does not allow you to add a review to your own post
    or to add a review to a post you have already reviewed.

    @param pid - The id of the post to add a review to.

    @return Either a JSON object with the status of the review or a 404
            if there is no post or a 400 if the user is not allowed to add a review
    """
    # This is a POST request.
    if request.method == "POST":
        check_self(pid)
        check_duplicate(pid)
        # with firebase_query("posts", [("id", "==", int(pid))]) as data:
        #     doc = data[0]
        #     # If the user is the user s uid
        #     if doc["user_uid"] == session["user"]["uid"]:
        #         return render_message(
        #             400, "You can't post a review on your own property"
        #         )
        # with firebase_query(
        #     "reviews",
        #     [
        #         ("reviewed", "==", int(pid)),
        #         ("reviewer", "==", session["user"]["uid"]),
        #     ],
        # ) as data:
        #     if len(data) > 0:
        #         return render_message(
        #             400, "You can't post a review on the same property twice"
        #         )
        data = {
            "rating": int(request.form["rating"]),
            "text": request.form["message"],
            "reviewer": session["user"]["uid"],
            "displayName": session["user"]["name"],
            "reviewed": int(pid),
            "timestamp": SERVER_TIMESTAMP,
        }
        add_to_firestore(data, "reviews")
        return redirect("/stays")
    return render_template("review.html")


@reviews.route("/review/edit/<int:rid>", methods=["GET", "POST"])
def edit_review(rid: int):
    """
    Edit a review. This is a view that allows you to edit an existing review. The user must be logged in and have permission to edit the review.

    @param rid - The id of the review to edit. This should be the same as the id of the review in the Firestore database.

    @return A template with the reviews. html template or a redirect to /stays if there is no review.
    """
    # This is a POST request to edit a review
    if request.method == "POST":
        data = {
            "rating": int(request.form["rating"]),
            "text": request.form["message"],
            "timestamp": SERVER_TIMESTAMP,
        }
        update_firestore(data, rid, "reviews")
        return redirect("/stays")
    else:
        with firebase_query("reviews", [("id", "==", int(rid))]) as data:
            try:
                doc = data[0]
                print(doc)
            except IndexError:
                return render_message(
                    404, "Cannot edit a review that doesn't exist"
                )
            return render_template("review.html", doc=doc)


@reviews.route("/review/delete/<int:rid>", methods=["GET"])
def delete_review(rid: int):
    """
    Delete a review from the database. If you try to delete a review that does not exist you will get a 400 error message.

    @param rid - id of the review to delete.

    @return template with error message or redirect to stays if the review is deleted.
    """
    with firebase_get(
        "reviews", f'{rid}|{session["user"]["uid"]}', partial=True
    ) as doc_ref:
        if doc_ref.get().to_dict() is None:
            return render_message(
                400, "Cannot delete a review that doesn't exist"
            )
        doc_ref.delete()
        return redirect("/stays")
