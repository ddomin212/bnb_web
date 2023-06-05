""" This module contains the views for the various listing pages of the website. """
from flask import Blueprint, render_template, redirect, request, session
from utils.countries import countries
from utils.firebase import get_avg_rating
from config import fetch_db
from utils.auth import login_required

main = Blueprint("main", __name__)


@main.context_processor
def inject_variables():
    """
    Inject variables into the template. This is used to create a dictionary
    that can be fed into the template as an argument to : func : ` get_variables `.


    @return A dictionary with variable names as keys and lists of values as values.
            Example :. { " countries " : [ " John " " British "
    """
    return {"countries": [c[0] for c in countries]}


@main.route("/")
def index():
    """
    Shows listings of current user. This is the page that is displayed when the
    user clicks on the index page.


    @return A template to render the listings page for index.
    """
    try:
        fav_doc = (
            fetch_db()
            .collection("fav")
            .document(session["user"]["uid"])
            .get()
            .to_dict()
        )
    except KeyError:
        fav_doc = []
    history = fetch_db().collection("posts").stream()
    docs = [doc.to_dict() for doc in history]
    # Calculate the average rating of each document
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=fav_doc, type="index")


@main.route("/favorites")
@login_required
def my_favs():
    """
    List favorites of the current user. This is a view to show the list of
    favorites of the current user.


    @return A template to render the listings page for favorites.
    """
    fav_doc = (
        fetch_db().collection("fav").document(session["user"]["uid"]).get().to_dict()
    )
    # If fav_doc is not available return 404
    if not fav_doc:
        return (
            render_template(
                "message.html", message="You have no favorites yet!", status_code=404
            ),
            404,
        )
    print(fav_doc)
    history = (
        fetch_db()
        .collection("posts")
        .where("id", "in", [int(i) for i in fav_doc["favs"]])
        .stream()
    )
    docs = [doc.to_dict() for doc in history]
    # Calculate the average rating of each property
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=fav_doc, type="index")


@main.route("/my-listings")
@login_required
def my_listings():
    """
    Listings of the logged in user. This is the page that lists rentals of the user.


    @return A template to render the listings page with a listings of the current user.
    """
    history = (
        fetch_db()
        .collection("posts")
        .where("user_uid", "==", session["user"]["uid"])
        .stream()
    )
    docs = [doc.to_dict() for doc in history]
    print(docs)
    # Calculate the average rating of each document
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=None, type="rentals")


@main.route("/listings/<uid>")
@login_required
def user_listings(uid):
    """
    Listings of a user. This is a view to display the listings of a user.

    @param uid - The id of the user

    @return A template for the listings of a user.
    """
    fav_doc = (
        fetch_db().collection("fav").document(session["user"]["uid"]).get().to_dict()
    )
    history = fetch_db().collection("posts").where("user_uid", "==", uid).stream()
    docs = [doc.to_dict() for doc in history]
    # Calculate the average rating of each document
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=fav_doc, type="index")


@main.route("/stays")
@login_required
def my_stays():
    """
    Listings of a user's stays. This is a view that allows to view the
    listings of a user and review them.

    @return A template for the stays of a user.
    """
    ref = (
        fetch_db()
        .collection("rentals")
        .where("user_uid", "==", session["user"]["uid"])
        .stream()
    )
    property_ids = [int(doc.to_dict()["property"]) for doc in ref]
    property_ref = (
        fetch_db().collection("posts").where("id", "in", property_ids).stream()
    )
    docs = [doc.to_dict() for doc in property_ref]
    # Calculate the average rating of each document
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))

    reviews_ref = (
        fetch_db()
        .collection("reviews")
        .where("reviewer", "==", session["user"]["uid"])
        .stream()
    )
    review_ids = [int(doc.to_dict()["reviewed"]) for doc in reviews_ref]

    return render_template(
        "listings.html", docs=docs, review_ids=review_ids, fav_doc=[], type="reviews"
    )


# Route for the property page


@main.route("/search", methods=["POST"])
def search():
    """
    Search for posts that match the given criteria. You can search by date range and price range, country or the maximum number of guests.


    @return A list of posts that match the search criteria. The list is sorted by price and with the most popular posts first
    """
    from utils.time import format_dates, format_firebase_date

    vfrom, to = format_dates(request.form["from"], request.form["to"])
    from_price = request.form["from-price"]
    to_price = request.form["to-price"]
    # if vfrom > to return error message
    if vfrom > to:
        return (
            render_template(
                "message.html", message="Invalid date range", status_code=400
            ),
            400,
        )
    # This function is used to check if the range is greater than the current price range
    if from_price > to_price:
        return (
            render_template(
                "message.html", message="Invalid price range", status_code=400
            ),
            400,
        )
    country = request.form["country"]
    guests = int(request.form["guests"])
    print(country, vfrom, to, guests)
    # Build the Firestore query
    query = (
        fetch_db()
        .collection("posts")
        .where("country", "==", country)
        .where("maxGuests", ">=", guests)
    )

    # Execute the query and print the results
    docs = query.stream()
    docs = [doc.to_dict() for doc in docs]
    docs = [
        doc
        for doc in docs
        if (doc["price"] >= int(from_price) and doc["price"] <= int(to_price))
        and (
            format_firebase_date(doc["from"]) <= vfrom
            and format_firebase_date(doc["to"]) >= to
        )
    ]
    # Calculate the average rating of each document
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, type="index")
