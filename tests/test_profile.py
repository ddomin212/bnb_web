""" This module contains tests for the profile view. """
from datetime import datetime
from unittest.mock import patch, MagicMock
from flask import session


def test_add_description(auth_client):
    """
    Test adding a description to the user's profile page.

    @param auth_client - An authenticated client to use for the test
    """
    # Set up test data
    phone = "555-555-5555"
    description = "This is a test description"
    uid = session["user"]["uid"]
    # Set up expected data
    expected_data = {"phone": phone, "description": description[:1000]}

    # Mock the Firebase admin auth module
    with patch("firebase_admin.auth.set_custom_user_claims") as mock_set_claims:
        # Make a request to the Flask route
        response = auth_client.post(
            "/user/add-info", data={"phone": phone, "description": description}
        )

        # Assert that the response is a redirect to the user's profile page
        assert response.status_code == 302
        assert response.headers["Location"] == f"/user/{uid}"

        # Assert that the mock function was called with the expected data
        mock_set_claims.assert_called_once_with(uid, expected_data)


def test_view_user(client, mocked_posts):
    """
    Test the view_user method. This is a test for the rating_view. py script.

    @param client - An authenticated client to use for the test
    @param mocked_posts - A list of mocked posts
    """
    # Set up test data
    uid = "test_user_id"
    user_data = {
        "display_name": "Test User",
        "email": "testuser@example.com",
        "uid": uid,
        "photo_url": "https://example.com/photo.jpg",
    }
    user = MagicMock()
    user.custom_claims = {"description": "Test description", "phone": "555-555-5555"}
    user.display_name = user_data["display_name"]
    user.email = user_data["email"]
    user.uid = user_data["uid"]
    user.photo_url = user_data["photo_url"]
    ratings_data = [
        {"rating": 5, "reviewed": "1", "reviewer": "1234", "timestamp": datetime.now()},
        {
            "rating": 4,
            "reviewed": "2",
            "reviewer": "1234",
            "timestamp": datetime.now(),
        },
    ]

    # Mock the Firebase admin auth module and the database fetch function
    with patch("firebase_admin.auth.get_user") as mock_get_user, patch(
        "firebase_admin.firestore.client"
    ) as mock_fetch_db:
        mock_get_user.return_value = user
        mocked_posts_dict = [MagicMock(to_dict=lambda: data) for data in mocked_posts]
        mocked_reviews = [MagicMock(to_dict=lambda: data) for data in ratings_data]

        mock_fetch_db.return_value.collection.return_value.where.return_value.stream.side_effect = [
            mocked_posts_dict,
            mocked_reviews,
            mocked_reviews,
            mocked_reviews,
            mocked_posts_dict,
            mocked_reviews,
        ]

        # Make a request to the Flask route
        response = client.get(f"/user/{uid}")

        # Assert that the response is a success and that the correct data is in the response context
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert b"Test User" in response.data
        assert b"Test description" in response.data
        assert b"555-555-5555" in response.data
        assert b"Brussels" in response.data
