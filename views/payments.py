""" This module contains the routes for Stripe payments. """
import os

import stripe
from flask import Blueprint, redirect, request, session
from google.cloud.exceptions import GoogleCloudError

from utils.auth import login_required
from utils.checks import check_self
from utils.render import render_message

payments = Blueprint("payments", __name__)


@payments.context_processor
def inject_variables():
    """
    Inject variables into script. This is useful for avoiding
    having to pass variables to every single template.


    @return dictionary of variables to inject into script as key and
            True or False as value depending on whether or not script is
    """
    return {"hidenav": True}


@payments.route("/payment/<pid>", methods=["POST"])
@login_required
def create_checkout_session(pid):
    """
    Create a payment session This is used to create a booking for a property.
    This route does not allow the user to book their own property.

    @param pid - The id of the post to be booked.

    @return A tuple of the form ( response status ) where response
            is a : class : ` stripe. checkout. Session `
    """
    check_self(pid)
    payment_session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price": "price_1MZWerIkzhBkf9zaHbc0qq2q",
                "quantity": 1,
            },
        ],
        success_url=f"""{os.environ["FLASK_URL"]}/payment-
                        success?session_id={"{CHECKOUT_SESSION_ID}"}""",
        cancel_url=f'{os.environ["FLASK_URL"]}/cancel',
    )
    session["user"]["verificationToken"] = payment_session.id
    session["user"]["pid"] = pid
    session["user"]["from"] = request.form["from"]
    session["user"]["to"] = request.form["to"]
    session["user"]["guests"] = request.form["guests"]
    return redirect(payment_session.url)


@payments.route("/payment-success", methods=["GET"])
@login_required
def success_payment():
    """
    If the user has paid successfully this view will add the user to firestore.
    Otherwise it will return an error message to the user.


    @return A view with success status and error message if there was an
            error or a redirect to the payment page
    """
    from utils.firebase import add_to_firestore

    payment_session_id = request.args.get("session_id")
    # This function is used to add a booking to firestore database.
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
        except GoogleCloudError:
            return render_message(500, "Internal server error")
        return render_message(200, "Payment successful")
    return render_message(401, "Unauthorized")
