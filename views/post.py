from flask import Blueprint, render_template, redirect, request, session, jsonify
from firebase_admin import storage
from utils.firebase import get_ratings_property
from utils.gpt import get_travel_tips
from config import fetch_db
from utils.auth import login_required
import os

posts = Blueprint("posts", __name__)


@posts.route("/view/<id>")
def view(id):
    history = fetch_db().collection("posts").where("id", "==", int(id)).stream()
    doc = [doc.to_dict() for doc in history][0]
    tags = []
    print(doc)
    [tags.append(item) for tag in [*doc["tags"]] for item in doc["tags"][tag]]
    reviews = get_ratings_property(id)
    review_ratings = [review["rating"] for review in reviews]
    print(reviews)
    avg_rating = (
        sum(review_ratings) / len(review_ratings) if len(review_ratings) > 0 else 0
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
    city = request.args.get("city")
    country = request.args.get("country")
    travel_tips = get_travel_tips(f"{city} + {', '} + {country}")
    if not travel_tips:
        return jsonify({"message": "Service not available"}), 200
    return jsonify({"travel_tips": travel_tips}), 200


@posts.route("/delete-img/<id>/<file>", methods=["GET"])
@login_required
def delete_img(id, file):
    doc_ref = fetch_db().collection("posts").document(f'{id}|{session["user"]["uid"]}')
    doc_data = doc_ref.get().to_dict()
    new_array = [x for x in doc_data["images"] if file not in x]
    doc_ref.update({"images": new_array})
    bucket = storage.bucket()
    file_to_delete = bucket.blob(f"static/uploads/{file}")
    file_to_delete.delete()
    return redirect(f"/add-6/{id}")


@posts.route("/delete/<id>", methods=["GET"])
@login_required
def delete_post(id):
    doc_ref = fetch_db().collection("posts").document(f'{id}|{session["user"]["uid"]}')
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
