""" This file contains all the functions that interact with the Firestore database. """
import os
from flask import current_app as app, session
from firebase_admin import storage
from werkzeug.utils import secure_filename
from config import fetch_db


def upload_to_bucket(filename):
    """
    Uploads a file to Firebase Storage. This is a convenience function for upload_to_bucket and upload_to_bucket_file

    @param filename - Name of file to upload

    @return URL of the uploaded file's public_url which can be used to retrieve the file after it has been
    """
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    return blob.public_url


def convert_date(date):
    """
    Convert a date string to a datetime object. This is useful for date parsing in the case of dates that don't have a timezone ( e. g.

    @param date - The date to convert. It can be in the format YYYY - MM - DD or YYYY - MM - DD.

    @return A datetime object representing the date and time specified by the date string. The time is set to the minimum time
    """
    from datetime import datetime

    return datetime.combine(
        datetime.strptime(date, "%Y-%m-%d").date(), datetime.min.time()
    )


def upload_images(request):
    """
    Uploads images to Firebase Storage. This is a wrapper around upload_to_bucket to
    allow upload of mutiple images to Firebase Storage

    @param request - The request that contains the list of images to upload.

    @return A list of URL's to the uploaded images. If there are no images an empty list is returned
    """
    urls = []
    uploaded_files = request.files.getlist("image", None)

    # Returns an array of images that are not in the request.
    if request.files.getlist("image") == []:
        return []

    # Returns a list of URLs to upload the uploaded files.
    for image_file in uploaded_files:
        # Returns a list of URLs to upload the image file to the upload folder.
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
    """
    Updates images for a post. This is used to upload images to Firebase Storage
    and remove them from the database document.

    @param request - Flask request object
    @param id - The id of the post to update

    @return A list of URLS that were uploaded
    """
    urls = []
    uploaded_files = request.files.getlist("image", None)

    # Returns a list of URLs to upload the uploaded files.
    for image_file in uploaded_files:
        # Returns a list of URLs to upload the image file to the upload folder.
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
    """
    Get the average rating of a proprety based on it's reviews.

    @param id - The id of the review
    @param testing - Whether or not we are testing the API

    @return The average rating or None if there are no reviews
    for the given id or if an error occurred
    """
    # Returns a list of all the reviews that have been reviewed.
    if not testing:
        reviews_ref = (
            fetch_db().collection("reviews").where("reviewed", "==", id).stream()
        )
        # [print(doc.to_dict()) for doc in reviews_ref]
    try:
        review_ids = [int(doc.to_dict()["rating"]) for doc in reviews_ref]
    except Exception:
        return None
    avg_rating = sum(review_ids) / len(review_ids) if len(review_ids) > 0 else None
    return avg_rating


def get_ratings_property(id):
    """
    Get ratings for a reviewed property. This is a list of dictionaries
    that contain information about the reviews.

    @param id - ID of the review. This can be any integer or a string
    that uniquely identifies a review.

    @return A list of dictionaries that contain information about the propetry reviews.
    """
    reviews_ref = (
        fetch_db().collection("reviews").where("reviewed", "==", int(id)).stream()
    )
    ratings = [doc.to_dict() for doc in reviews_ref]
    return ratings


def get_ratings_user(uid):
    """
    Get ratings for a user among all his properties.
    This is a list of dictionaries with one dictionary per review.

    @param uid - user id to get ratings for

    @return list of dictionaries with one dictionary per review or an
    empty list if there are no ratings for the user.
    """
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
    """
    Add a document to firestore.

    @param data - The data to add to firestore. It should be a dictionary.
    """
    # Get a reference to the document collection
    ref = fetch_db().collection(collection)
    count = len(ref.get()) + 1
    data["id"] = count
    session["user"]["creation_id"] = count
    # Create a document
    doc_ref = ref.document(str(count) + "|" + str(session["user"]["uid"]))
    doc_ref.set(data)


def update_firestore(data, id, collection, images=False):
    """
    Update a document in Firestore.

    @param data - The data to update.
    @param id - The id of the document that needs to be updated.
    @param collection - The collection to update the document in.
    @param images - If True add the images to the document. If False add the images
    """
    # Get a reference to the document collection
    doc_ref = (
        fetch_db().collection(collection).document(f'{id}|{session["user"]["uid"]}')
    )
    # Add images to the images array
    if images is True:
        doc_data = doc_ref.get().to_dict()
        try:
            data["images"] += doc_data["images"]
        except Exception:
            pass
    doc_ref.update(data)


def add_favorite(data):
    """
    Add a favourite to the user's favorites.

    @param data - The property to add to the user's favorites

    @return 404 if the user does not exist or 200 if the operation was successful
    """
    try:
        ref = fetch_db().collection("fav")
        doc_ref = ref.document(session["user"]["uid"])
        doc_ref.set(data)
        return "Success", 200
    except Exception:
        return Exception, 404


def update_favorites(data):
    """
    Update favorites for the current user. This will update the
    user's favorite list with the data provided

    @param data - A dictionary containing the data to update

    @return 404 if the user does not exist or 200 if the operation was successful
    """
    # Get a reference to the document collection
    try:
        doc_ref = fetch_db().collection("fav").document(session["user"]["uid"])
        doc_ref.update(data)
    except Exception:
        return Exception, 404


def allowed_file(filename):
    """
    Checks if filename is allowed to be uploaded. This is a case insensitive check
    to make sure we don't accidentally upload files with different extensions

    @param filename - The filename to check.

    @return True if the filename is allowed False otherwise. Note that the
    extension must be lower case
    """
    allowed_extensions = ["png", "jpg", "jpeg", "gif", "webp"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
