""" This module contains tests for the Stripe payment routes. """
from unittest.mock import patch, MagicMock
from flask import session


def test_create_checkout_session(auth_client, mocked_posts):
    """
    Create a test for the create checkout session route. This test will mock the database and Stripe API calls.

    @param auth_client - An authentificated client to make requests with
    @param mocked_posts - A list of mocked posts
    """
    # Create a test client using Flask's test_client() method
    with patch("firebase_admin.firestore.client") as firestore, patch(
        "stripe.checkout.Session.create"
    ) as stripe:
        firestore.return_value.collection.return_value.where.return_value.stream.return_value = [
            MagicMock(to_dict=lambda: mocked_posts[0])
        ]
        # Mock the Stripe checkout session creation
        stripe.return_value = MagicMock(url="https://example.com/checkout", id="123")

        # Make a POST request to the route with parameters
        response = auth_client.post(
            "/payment/1",
            data={"from": "2023-05-01", "to": "2023-05-07", "guests": "2"},
        )

        # Assert the response status code
        assert response.status_code == 302

        # Assert the redirect location
        assert session["user"]["verificationToken"] == "123"
        assert session["user"]["pid"] == "1"
        assert session["user"]["from"] == "2023-05-01"
        assert session["user"]["to"] == "2023-05-07"
        assert session["user"]["guests"] == "2"
        assert response.headers["Location"] == "https://example.com/checkout"


def test_success_payment(auth_client):
    """
    Test the success route for payment. This is a test to make sure we can get the
    verification token and redirect to the payment page

    @param auth_client - An authenticated Firestore client
    """
    # Mock the request.args.get() method
    with patch("firebase_admin.firestore.client"):
        # Make a GET request to the route
        response = auth_client.get("/payment-success?session_id=testing")
        # Assert the response status code
        assert response.status_code == 200
        assert session["user"]["verificationToken"] == "testing"
        # Assert the rendered template
        assert "Payment successful" in response.data.decode("utf-8")
