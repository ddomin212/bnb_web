from contextlib import contextmanager
from typing import Any, List, Tuple

from .setup import connect_to_firestore
from google.cloud.exceptions import GoogleCloudError
from utils.render import render_message
from flask import session

@contextmanager
def firebase_query(collection: str, query: List[Tuple[str, str, Any]]):
    """
    Query Firebase and return a generator. This is a generator that can be used to iterate over a collection and query the Firebase database.

    @param collection - The name of the collection to query. It must exist.
    @param query - The query to execute. It can be a list of tuples or a single tuple, as per the Firestore API.

    @return An iterable of documents that match the query or a 500 if there is a problem connecting to the database.
    """
    # Convert a query to a list of query tuples.
    if isinstance(query, tuple):
        query = [query]
    try:
        docs = connect_to_firestore().collection(collection)
        # Find all documents that match the given query.
        for q in query:
            retyped = (
                q[2]
                if isinstance(q[2], List) or isinstance(q[2], str)
                else int(q[2])
            )
            docs = docs.where(q[0], q[1], retyped)
        docs = docs.stream()
        yield [doc.to_dict() for doc in docs]
    except GoogleCloudError:
        return render_message(500, "Cannot connect to database.")


@contextmanager
def firebase_get(collection: str, name: str, partial: bool = False):
    """
    Get a document from Firebase. This is a generator that yields the document in dict form.

    @param collection - The name of the collection to retrieve from.
    @param name - The name of the document to retrieve.
    @param partial - If True the document will be returned as a Firestore object rather than a dict.

    @return A dict containing the document or a 500 if there is an error connecting to the database.
    """
    try:
        doc = connect_to_firestore().collection(collection).document(name)
        # Yields a dictionary of the document.
        if partial:
            yield doc
        else:
            yield doc.get().to_dict()
    except GoogleCloudError:
        return render_message(500, "Cannot connect to database.")
    
def get_avg_rating(id):
    """
    Get the average rating of a proprety based on it's reviews.

    @param id - The id of the review
    @param testing - Whether or not we are testing the API

    @return The average rating or None if there are no reviews
    for the given id or if an error occurred
    """
    # Returns a list of all the reviews that have been reviewed.
    try:
        reviews_ref = (
            connect_to_firestore()
            .collection("reviews")
            .where("reviewed", "==", id)
            .stream()
        )
        review_ids = [int(doc.to_dict()["rating"]) for doc in reviews_ref]
    except GoogleCloudError:
        return None
    avg_rating = (
        sum(review_ids) / len(review_ids) if len(review_ids) > 0 else None
    )
    return avg_rating


def get_avg_ratings(docs):
    """
    Get the average ratings for a list of documents. This is a convenience function for get_avg_rating.

    @param docs - A list of documents to get the average ratings for

    @return docs - The list of documents with the average ratings added to them
    """

    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return docs


def get_ratings_property(id):
    """
    Get ratings for a reviewed property. This is a list of dictionaries
    that contain information about the reviews.

    @param id - ID of the review. This can be any integer or a string
    that uniquely identifies a review.

    @return A list of dictionaries that contain information about the propetry reviews.
    """
    reviews_ref = (
        connect_to_firestore()
        .collection("reviews")
        .where("reviewed", "==", int(id))
        .stream()
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
    try:
        posts_ref = (
            connect_to_firestore()
            .collection("posts")
            .where("user_uid", "==", uid)
            .stream()
        )
        user_posts = [int(doc.to_dict()["id"]) for doc in posts_ref]
        reviews_ref = (
            connect_to_firestore()
            .collection("reviews")
            .where("reviewed", "in", user_posts)
            .stream()
        )
        reviews = [doc.to_dict() for doc in reviews_ref]
        ratings = [review["rating"] for review in reviews]
        avg_rating = sum(ratings) / len(ratings) if len(ratings) > 0 else 0
    except GoogleCloudError:
        return []
    return reviews, avg_rating


def add_to_firestore(data, collection):
    """
    Add a document to firestore.

    @param data - The data to add to firestore. It should be a dictionary.
    """
    # Get a reference to the document collection
    ref = connect_to_firestore().collection(collection)
    count = len(ref.get()) + 1
    data["id"] = count
    session["user"]["creation_id"] = count
    # Create a document
    doc_ref = ref.document(str(count) + "|" + str(session["user"]["uid"]))
    doc_ref.set(data)


def update_firestore(data, did, collection, images=False):
    """
    Update a document in Firestore.

    @param data - The data to update.
    @param id - The id of the document that needs to be updated.
    @param collection - The collection to update the document in.
    @param images - If True add the images to the document. If False add the images
    """
    # Get a reference to the document collection
    doc_ref = (
        connect_to_firestore()
        .collection(collection)
        .document(f'{did}|{session["user"]["uid"]}')
    )
    # Add images to the images array
    if images is True:
        doc_data = doc_ref.get().to_dict()
        try:
            data["images"] += doc_data["images"]
        except GoogleCloudError:
            pass
    doc_ref.update(data)


def add_favorite(data):
    """
    Add a favourite to the user's favorites.

    @param data - The property to add to the user's favorites

    @return 404 if the user does not exist or 200 if the operation was successful
    """
    try:
        ref = connect_to_firestore().collection("fav")
        doc_ref = ref.document(session["user"]["uid"])
        doc_ref.set(data)
        return "Success", 200
    except GoogleCloudError:
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
        doc_ref = connect_to_firestore().collection("fav").document(session["user"]["uid"])
        doc_ref.update(data)
    except GoogleCloudError:
        return Exception, 404