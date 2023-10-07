""" This file contains all the functions that interact with the Firestore database. """
import os
from flask import Request
from .setup import connect_to_firestore
from firebase_admin import storage
from flask import current_app as app
from flask import session
from werkzeug.utils import secure_filename


def upload_to_bucket(filename: str):
    """
    Uploads a file to Firebase Storage. This is a convenience function for upload_to_bucket and upload_to_bucket_file

    @param filename - Name of file to upload

    @return URL of the uploaded file's public_url which can be used to retrieve the file after it has been
    """
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    return blob.public_url


def upload_images(request: Request):
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
            url = upload_to_bucket(
                "/".join([app.config["UPLOAD_FOLDER"], filename])
            )
            os.remove("/".join([app.config["UPLOAD_FOLDER"], filename]))
            urls.append(url)
        else:
            return []
    return urls


def update_images(request: Request, id: int):
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
            url = upload_to_bucket(
                "/".join([app.config["UPLOAD_FOLDER"], filename])
            )
            os.remove("/".join([app.config["UPLOAD_FOLDER"], filename]))
            urls.append(url)
        else:
            return []

    doc_ref = (
        connect_to_firestore()
        .collection("posts")
        .document(f'{id}|{session["user"]["uid"]}')
    )
    doc_data = doc_ref.get().to_dict()
    new_urls = doc_data["images"] + urls

    return new_urls


def allowed_file(filename: str):
    """
    Checks if filename is allowed to be uploaded. This is a case insensitive check
    to make sure we don't accidentally upload files with different extensions

    @param filename - The filename to check.

    @return True if the filename is allowed False otherwise. Note that the
    extension must be lower case
    """
    allowed_extensions = ["png", "jpg", "jpeg", "gif", "webp"]
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )
