from flask import Blueprint, render_template, redirect, request, session, jsonify
from firebase_admin import auth
from utils.countries import countries
from config import fetch_db
from utils.auth import login_required
import stripe
import os

payments = Blueprint("payments", __name__)


@payments.context_processor
def inject_variables():
    return {"hidenav": True}


@payments.route("/payment/<pid>", methods=["POST"])
@login_required
def create_checkout_session(pid):
    self_review = fetch_db().collection("posts").where("id", "==", int(pid)).stream()
    doc = [doc.to_dict() for doc in self_review][0]
    if doc["user_uid"] == session["user"]["uid"]:
        return (
            render_template(
                "message.html",
                error_message="You can't rent your own property",
                status_code=400,
            ),
            400,
        )
    payment_session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price": "price_1MZWerIkzhBkf9zaHbc0qq2q",
                "quantity": 1,
            },
        ],
        success_url=f'{os.environ["FLASK_URL"]}/payment-success?session_id={"{CHECKOUT_SESSION_ID}"}',
        cancel_url=f'{os.environ["FLASK_URL"]}/cancel',
    )
    session.get("user")["verificationToken"] = payment_session.id
    session["user"]["pid"] = pid
    session["user"]["from"] = request.form["from"]
    session["user"]["to"] = request.form["to"]
    session["user"]["guests"] = request.form["guests"]
    print(session["user"])
    return redirect(payment_session.url)


@payments.route("/payment-success", methods=["GET"])
@login_required
def success_payment():
    from utils.firebase import add_to_firestore

    payment_session_id = request.args.get("session_id")
    print(session["user"])
    if payment_session_id == session["user"]["verificationToken"]:
        try:
            add_to_firestore(
                {
                    "user_uid": session["user"]["uid"],
                    "pay_id": payment_session_id,
                    "property": int(session["user"]["pid"]),
                    "guests": int(session["user"]["guests"]),
                    "from": session["user"]["from"],
                    "to": session["user"]["to"],
                },
                "rentals",
            )
        except Exception as e:
            print(e)
        return (
            render_template(
                "message.html", error_message="Payment successful", status_code=""
            ),
            200,
        )
    else:
        return (
            render_template(
                "message.html", error_message="Unauthorized access", status_code=401
            ),
            401,
        )
