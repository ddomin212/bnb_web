from flask import Blueprint, render_template, redirect, request, session, jsonify
import os
from utils.countries import countries
from utils.firebase import get_avg_rating
from config import fetch_db
from utils.auth import login_required

main = Blueprint("main", __name__)


@main.context_processor
def inject_variables():
    return {"countries": [c[0] for c in countries]}


@main.route("/")
def index():
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
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=fav_doc, type="index")


@main.route("/favorites")
@login_required
def my_favs():
    fav_doc = (
        fetch_db().collection("fav").document(session["user"]["uid"]).get().to_dict()
    )
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
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=fav_doc, type="index")


@main.route("/my-listings")
@login_required
def my_listings():
    history = (
        fetch_db()
        .collection("posts")
        .where("user_uid", "==", session["user"]["uid"])
        .stream()
    )
    docs = [doc.to_dict() for doc in history]
    print(docs)
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=None, type="rentals")


@main.route("/listings/<uid>")
@login_required
def user_listings(uid):
    fav_doc = (
        fetch_db().collection("fav").document(session["user"]["uid"]).get().to_dict()
    )
    history = fetch_db().collection("posts").where("user_uid", "==", uid).stream()
    docs = [doc.to_dict() for doc in history]
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, fav_doc=fav_doc, type="index")


@main.route("/stays")
@login_required
def my_stays():
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
    from utils.time import format_dates, format_firebase_date

    vfrom, to = format_dates(request.form["from"], request.form["to"])
    from_price = request.form["from-price"]
    to_price = request.form["to-price"]
    if vfrom > to:
        return (
            render_template(
                "message.html", message="Invalid date range", status_code=400
            ),
            400,
        )
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
    for doc in docs:
        doc["avg_rating"] = get_avg_rating(int(doc["id"]))
    return render_template("listings.html", docs=docs, type="index")
