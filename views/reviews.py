""" This file contains the views for reviews. It allows you to add, edit and delete reviews. """
from flask import Blueprint, render_template, redirect, request, session
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from utils.firebase import add_to_firestore, update_firestore
from config import fetch_db

reviews = Blueprint("reviews", __name__)


@reviews.route("/review/add/<pid>", methods=["GET", "POST"])
def add_review(pid):
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
        self_review = (
            fetch_db().collection("posts").where("id", "==", int(pid)).stream()
        )
        try:
            doc = [doc.to_dict() for doc in self_review][0]
        except IndexError:
            return (
                render_template(
                    "message.html",
                    error_message="Cannot check for duplicate (no posts)",
                    status_code=404,
                ),
                404,
            )
        # If the user is the user s uid
        if doc["user_uid"] == session["user"]["uid"]:
            return (
                render_template(
                    "message.html",
                    error_message="You can't post a review on your own property",
                    status_code=400,
                ),
                400,
            )
        duplicate = (
            fetch_db()
            .collection("reviews")
            .where("reviewed", "==", int(pid))
            .where("reviewer", "==", session["user"]["uid"])
            .stream()
        )
        duplicates = [doc.to_dict() for doc in duplicate]
        # If there are duplicate values in the list return a 400 error message.
        if len(duplicates) > 0:
            return (
                render_template(
                    "message.html",
                    error_message="You can't post a review on the same property twice",
                    status_code=400,
                ),
                400,
            )

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
    else:
        return render_template("review.html")


@reviews.route("/review/edit/<rid>", methods=["GET", "POST"])
def edit_review(rid):
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
        history = fetch_db().collection("reviews").where("id", "==", int(rid)).stream()
        try:
            doc = [doc.to_dict() for doc in history][0]
        except IndexError:
            return (
                render_template(
                    "message.html",
                    error_message="Cannot edit a review that doesn't exist",
                    status_code=400,
                ),
                400,
            )
        return render_template("review.html", doc=doc)


@reviews.route("/review/delete/<rid>", methods=["GET"])
def delete_review(rid):
    """
    Delete a review from the database. If you try to delete a review that does not exist you will get a 400 error message.

    @param rid - id of the review to delete.

    @return template with error message or redirect to stays if the review is deleted.
    """
    doc_ref = (
        fetch_db().collection("reviews").document(f'{rid}|{session["user"]["uid"]}')
    )
    # If the doc_ref is not a review or the user has not been deleted.
    if doc_ref.get().to_dict() is None:
        return (
            render_template(
                "message.html",
                error_message="You can't delete a review that doesn't exist",
                status_code=400,
            ),
            400,
        )
    doc_ref.delete()
    return redirect("/stays")
