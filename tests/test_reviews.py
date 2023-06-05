""" Tests for the reviews blueprint. """
from unittest.mock import patch, Mock
from flask import session


def test_add_review_success(auth_client):
    """
    Test adding a review with valid data.

    @param auth_client - An authenticated client to use for testing
    """
    # Mock the Firestore queries
    with patch("firebase_admin.firestore.client") as firestore_mock:
        # Mock the database query to return posts for the user's favorites
        mock_history = [
            {
                "id": "1",
                "city": "Tirana",
                "country": "Albania",
                "price": 10,
                "user_uid": "123589",
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=post)) for post in mock_history
        ]

        mock_reviews = []
        firestore_mock.return_value.collection.return_value.document.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        # Make a GET request to render the review form
        response = auth_client.post(
            "/review/add/1", data={"rating": "4", "message": "Lorem Ipsum"}
        )
        # Verify that the response is a redirect
        assert response.status_code == 302
        assert response.headers["Location"] == "/stays"
    # Make a GET request to render the review form
    response = auth_client.get("/review/add/123")

    # Verify that the response contains the review form
    assert response.status_code == 200
    assert b'<form method="post" id="review-form"' in response.data


def test_add_review_self(auth_client):
    """
    Test adding a review to the current user's property.

    @param auth_client - An authenticated client to use for testing
    """
    # Mock the Firestore queries
    with patch("firebase_admin.firestore.client") as firestore_mock:
        # Mock the database query to return posts for the user's favorites
        mock_history = [
            {
                "id": "1",
                "city": "Tirana",
                "country": "Albania",
                "price": 10,
                "user_uid": session["user"]["uid"],
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=post)) for post in mock_history
        ]

        mock_reviews = []
        firestore_mock.return_value.collection.return_value.document.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        # Make a GET request to render the review form
        response = auth_client.post(
            "/review/add/1", data={"rating": "4", "message": "Lorem Ipsum"}
        )
        # Verify that the response is a redirect
        assert response.status_code == 400
        assert b"post a review on your own property" in response.data


def test_add_review_duplicate(auth_client):
    """
    Test adding a review that already exists.

    @param auth_client - An authenticated client to use for testing
    """
    # Mock the Firestore queries
    with patch("firebase_admin.firestore.client") as firestore_mock:
        # Mock the database query to return posts for the user's favorites
        mock_history = [
            {
                "id": 1,
                "city": "Tirana",
                "country": "Albania",
                "price": 10,
                "user_uid": "12358",
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=post)) for post in mock_history
        ]

        mock_reviews = [
            {
                "rating": "4",
                "message": "Lorem Ipsum",
                "reviewer": session["user"]["uid"],
                "reviewed": 1,
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        # Make a GET request to render the review form
        response = auth_client.post(
            "/review/add/1", data={"rating": "4", "message": "Lorem Ipsum"}
        )
        # Verify that the response is a redirect
        assert response.status_code == 400
        assert b"post a review on the same property twice" in response.data


def test_edit_review_post(auth_client):
    """
    Test editing a review with valid data.

    @param auth_client - An authenticated client to use for testing
    """
    # Mock the Firestore queries
    with patch("firebase_admin.firestore.client") as firestore_mock:
        # Mock the database query to return posts for the user's favorites
        mock_history = [
            {
                "id": "1",
                "city": "Tirana",
                "country": "Albania",
                "price": 10,
                "user_uid": session["user"]["uid"],
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=post)) for post in mock_history
        ]

        mock_reviews = [
            {
                "rating": "4",
                "id": 4,
                "message": "Lorem Ipsum",
                "reviewer": session["user"]["uid"],
                "reviewed": 1,
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        # Make a GET request to render the review form
        response = auth_client.post(
            "/review/edit/4", data={"rating": "3", "message": "Lorem Ipsum"}
        )
        # Verify that the response is a redirect

        assert response.status_code == 302
        assert response.headers["Location"] == "/stays"
        # Make a GET request to render the review form


def test_edit_review_get(auth_client):
    """
    Test the edit review form.

    @param auth_client - An authenticated client to use for testing
    """
    with patch("firebase_admin.firestore.client") as firestore_mock:
        mock_reviews = [
            {
                "rating": "4",
                "id": 4,
                "text": "Lorem Ipsum",
                "reviewer": session["user"]["uid"],
                "reviewed": 1,
            }
        ]
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        response = auth_client.get("/review/edit/4")
        # print(response.data.decode("utf-8"))
        # Verify that the response contains the review form
        assert response.status_code == 200
        assert b"Lorem Ipsum</textarea" in response.data
        assert b'const valueToSelect = "4"' in response.data


def test_edit_review_get_not_exist(auth_client):
    """
    Test that editing a review that does not exist returns a 400 error.

    @param auth_client - An authenticated client to use for testing.
    """
    with patch("firebase_admin.firestore.client") as firestore_mock:
        mock_reviews = []
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        response = auth_client.get("/review/edit/4")
        assert response.status_code == 400
        assert b"Cannot edit a review that" in response.data


def test_delete_review(auth_client):
    """
    Test deleting a review.

    @param auth_client - An authenticated client to use for testing.
    """
    with patch("firebase_admin.firestore.client") as firestore_mock:
        mock_reviews = [
            {
                "rating": "4",
                "id": 4,
                "text": "Lorem Ipsum",
                "reviewer": session["user"]["uid"],
                "reviewed": 1,
            }
        ]
        firestore_mock.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in mock_reviews
        ]
        response = auth_client.get("/review/delete/4")
        assert response.status_code == 302
        assert response.headers["Location"] == "/stays"


def test_delete_review_not_exist(auth_client):
    """
    Test that delete a review that does not exist returns 400 error.

    @param auth_client - An authenticated client to use for testing.
    """
    with patch("firebase_admin.firestore.client") as firestore_mock:
        firestore_mock.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = (
            None
        )
        response = auth_client.get("/review/delete/4")
        assert response.status_code == 400
        assert b"delete a review that doesn" in response.data
