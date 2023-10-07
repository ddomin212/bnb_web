""" This module contains the views for the various listing pages of the website. """
from flask import Blueprint, redirect, render_template, request, session
from utils.auth import login_required
from utils.countries import countries
from components.firebase.database import firebase_get, firebase_query, get_avg_ratings
from utils.render import render_message
from utils.search import get_search_params
from utils.render import error_handler

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
@error_handler
def index():
    """
    Shows listings of current user. This is the page that is displayed when the
    user clicks on the index page.


    @return A template to render the listings page for index.
    """
    with firebase_query("posts", []) as docs:
        docs = get_avg_ratings(docs)
        if "user" not in session:
            return render_template(
                "listings.html", docs=docs, fav_doc=[], type="index"
            )

        with firebase_get("fav", session["user"]["uid"]) as fav_doc:
            return render_template(
                "listings.html", docs=docs, fav_doc=fav_doc, type="index"
            )


@main.route("/favorites")
@login_required
@error_handler
def my_favs():
    """
    List favorites of the current user. This is a view to show the list of
    favorites of the current user.


    @return A template to render the listings page for favorites.
    """
    with firebase_get("fav", session["user"]["uid"]) as fav_doc:
        # If fav_doc is not available return 404
        if not fav_doc:
            return render_message(404, "You have no favorites")
        with firebase_query(
            "posts", [("id", "in", [int(i) for i in fav_doc["favs"]])]
        ) as docs:
            # Calculate the average rating of each property
            docs = get_avg_ratings(docs)
            return render_template(
                "listings.html", docs=docs, fav_doc=fav_doc, type="index"
            )


@main.route("/my-listings")
@login_required
@error_handler
def my_listings():
    """
    Listings of the logged in user. This is the page that lists rentals of the user.


    @return A template to render the listings page with a listings of the current user.
    """
    with firebase_query(
        "posts", [("user_uid", "==", session["user"]["uid"])]
    ) as docs:
        docs = get_avg_ratings(docs)
        return render_template(
            "listings.html", docs=docs, fav_doc=None, type="rentals"
        )


@main.route("/listings/<uid>")
@login_required
@error_handler
def user_listings(uid):
    """
    Listings of a user. This is a view to display the listings of a user.

    @param uid - The id of the user

    @return A template for the listings of a user.
    """
    with firebase_get(
        "fav", session["user"]["uid"]
    ) as fav_doc, firebase_query("posts", [("user_uid", "==", uid)]) as docs:
        docs = get_avg_ratings(docs)
        return render_template(
            "listings.html", docs=docs, fav_doc=fav_doc, type="index"
        )


@main.route("/stays")
@login_required
@error_handler
def my_stays():
    """
    Listings of a user's stays. This is a view that allows to view the
    listings of a user and review them.

    @return A template for the stays of a user.
    """
    with firebase_query(
        "rentals", [("user_uid", "==", session["user"]["uid"])]
    ) as properties, firebase_query(
        "posts", [("id", "in", [int(doc["property"]) for doc in properties])]
    ) as docs, firebase_query(
        "reviews", [("reviewer", "==", session["user"]["uid"])]
    ) as reviews:
        docs = get_avg_ratings(docs)
        review_ids = [int(doc["reviewed"]) for doc in reviews]

        return render_template(
            "listings.html",
            docs=docs,
            review_ids=review_ids,
            fav_doc=[],
            type="reviews",
        )


# Route for the property page


@main.route("/search", methods=["POST"])
@error_handler
def search():
    """
    Search for posts that match the given criteria. You can search by date range and price range, country or the maximum number of guests.


    @return A list of posts that match the search criteria. The list is sorted by price and with the most popular posts first
    """
    from utils.time import format_firebase_date

    vfrom, to, from_price, to_price, country, guests = get_search_params(
        request
    )

    if vfrom > to:
        return render_message(400, "Invalid date range")
    if from_price > to_price:
        return render_message(400, "Invalid price range")

    # Build the Firestore query
    with firebase_query(
        "posts", [("country", "==", country), ("maxGuests", ">=", guests)]
    ) as docs:
        # Filter the documents by price and date range, since we are limited in what
        # we can do with Firestore queries
        docs = [
            doc
            for doc in docs
            if (
                doc["price"] >= int(from_price)
                and doc["price"] <= int(to_price)
            )
            and (
                format_firebase_date(doc["from"]) <= vfrom
                and format_firebase_date(doc["to"]) >= to
            )
        ]
        # Calculate the average rating of each document
        docs = get_avg_ratings(docs)
        return render_template("listings.html", docs=docs, type="index")
