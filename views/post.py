""" This module contains the view functions for the property page. """
from firebase_admin import storage
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
)
from utils.auth import login_required
from utils.firebase import firebase_get, firebase_query, get_ratings_property
from utils.gpt import get_travel_tips

posts = Blueprint("posts", __name__)


@posts.route("/view/<int:pid>")
def view(pid: int):
    """
    View a property. This is the view function for the property page. It returns a list of properties that match the
    pid and the average rating of the reviews in the property

    @param pid - The pid of the property to view

    @return The HTML of the property page. This page contains the property's information, reviews, and travel tips.
    """
    with firebase_query("posts", [("id", "==", int(pid))]) as data:
        doc = data[0]
        tags = []
        # Add tags to the tags list
        for tag in [*doc["tags"]]:
            for item in doc["tags"][tag]:
                tags.append(item)
        reviews = get_ratings_property(pid)
        review_ratings = [review["rating"] for review in reviews]
        avg_rating = (
            sum(review_ratings) / len(review_ratings)
            if len(review_ratings) > 0
            else 0
        )
        return render_template(
            "property.html",
            doc=doc,
            reviews=reviews,
            avg_rating=avg_rating,
            travel_tips=[],
            tags=tags[:8],
        )


@posts.route("/tips", methods=["GET"])
def get_tips():
    """
    Get list of tips for what to visit in a city using Bing Search AI.

    @return JSON with list of tips or error message Bing Search AI is not available
    """
    city = request.args.get("city")
    country = request.args.get("country")
    travel_tips = get_travel_tips(f"{city} + {', '} + {country}")
    # This method is used to check for tips. If there are no tips, then the service is not available
    if not travel_tips:
        return jsonify({"message": "Service not available"}), 200
    return jsonify({"travel_tips": travel_tips}), 200


@posts.route("/delete-img/<int:pid>/<string:file>", methods=["GET"])
@login_required
def delete_img(pid: int, file: str):
    """
    Delete image from post. This will be used by JS call to delete an image from a post.

    @param id - id of the post to delete the image from
    @param file - name of the image to delete. It must be in the
               static / uploads folder of the firebase storage.

    @return redirect to Add images page after deleting the image from the post.
    """
    with firebase_get(
        "posts", f"{pid}|{session['user']['uid']}", partial=True
    ) as doc_ref:
        doc_data = doc_ref.get().to_dict()
        new_array = [x for x in doc_data["images"] if file not in x]
        doc_ref.update({"images": new_array})
        bucket = storage.bucket()
        file_to_delete = bucket.blob(f"static/uploads/{file}")
        file_to_delete.delete()
        return redirect(f"/add-6/{pid}")


@posts.route("/delete/<int:pid>", methods=["GET"])
@login_required
def delete_post(pid: int):
    """
    Delete a post from the database. This is a view for
    deleting a post and redirecting to the home page

    @param id - The id of the post to delete

    @return A template to render if the deletion was successful or a
            404 if there was a problem with the deletion
    """
    with firebase_get(
        "posts", f"{pid}|{session['user']['uid']}", partial=True
    ) as doc_ref:
        print(doc_ref.get().exists)
        if not doc_ref.get().exists:
            return (
                render_template(
                    "message.html",
                    error_message="Can't delete a post that does not exist!",
                    status_code=404,
                ),
                404,
            )
        doc_ref.delete()
        return redirect("/")
