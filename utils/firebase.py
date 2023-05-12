import os
from flask import current_app as app, session
from firebase_admin import storage
from werkzeug.utils import secure_filename
from config import fetch_db


def upload_to_bucket(filename):
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    return blob.public_url


def convert_date(date):
    from datetime import datetime

    return datetime.combine(
        datetime.strptime(date, "%Y-%m-%d").date(), datetime.min.time()
    )


def upload_images(request):
    urls = []
    uploaded_files = request.files.getlist("image", None)

    if request.files.getlist("image") == []:
        return []

    for image_file in uploaded_files:
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save("/".join([app.config["UPLOAD_FOLDER"], filename]))
            url = upload_to_bucket("/".join([app.config["UPLOAD_FOLDER"], filename]))
            os.remove("/".join([app.config["UPLOAD_FOLDER"], filename]))
            urls.append(url)
        else:
            return []
    return urls


def update_images(request, id):
    urls = []
    uploaded_files = request.files.getlist("image", None)

    for image_file in uploaded_files:
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save("/".join([app.config["UPLOAD_FOLDER"], filename]))
            url = upload_to_bucket("/".join([app.config["UPLOAD_FOLDER"], filename]))
            os.remove("/".join([app.config["UPLOAD_FOLDER"], filename]))
            urls.append(url)
        else:
            return []

    doc_ref = fetch_db().collection("posts").document(f'{id}|{session["user"]["uid"]}')
    doc_data = doc_ref.get().to_dict()
    new_urls = doc_data["images"] + urls

    return new_urls


def get_avg_rating(id, testing=False):
    if not testing:
        reviews_ref = (
            fetch_db().collection("reviews").where("reviewed", "==", id).stream()
        )
        review_ids = [print(doc.to_dict()) for doc in reviews_ref]
    try:
        review_ids = [int(doc.to_dict()["rating"]) for doc in reviews_ref]
    except Exception:
        return None
    avg_rating = sum(review_ids) / len(review_ids) if len(review_ids) > 0 else None
    return avg_rating


def get_ratings_property(id):
    reviews_ref = (
        fetch_db().collection("reviews").where("reviewed", "==", int(id)).stream()
    )
    ratings = [doc.to_dict() for doc in reviews_ref]
    return ratings


def get_ratings_user(uid):
    posts_ref = fetch_db().collection("posts").where("user_uid", "==", uid).stream()
    user_posts = [int(doc.to_dict()["id"]) for doc in posts_ref]
    reviews_ref = (
        fetch_db().collection("reviews").where("reviewed", "in", user_posts).stream()
    )
    try:
        ratings = [doc.to_dict() for doc in reviews_ref]
    except Exception:
        return []
    return ratings


def add_to_firestore(data, collection):
    # Get a reference to the document collection
    ref = fetch_db().collection(collection)
    count = len(ref.get()) + 1
    data["id"] = count
    session["user"]["creation_id"] = count
    # Create a document
    doc_ref = ref.document(str(count) + "|" + str(session["user"]["uid"]))
    doc_ref.set(data)


def update_firestore(data, id, collection, images=False):
    # Get a reference to the document collection
    doc_ref = (
        fetch_db().collection(collection).document(f'{id}|{session["user"]["uid"]}')
    )
    if images == True:
        doc_data = doc_ref.get().to_dict()
        try:
            data["images"] += doc_data["images"]
        except Exception:
            pass
    doc_ref.update(data)


def add_favorite(data):
    try:
        ref = fetch_db().collection("fav")
        doc_ref = ref.document(session["user"]["uid"])
        doc_ref.set(data)
    except Exception:
        return Exception, 404


def update_favorites(data):
    # Get a reference to the document collection
    try:
        doc_ref = fetch_db().collection("fav").document(session["user"]["uid"])
        doc_ref.update(data)
    except Exception:
        return Exception, 404


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
