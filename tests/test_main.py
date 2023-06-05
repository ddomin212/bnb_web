""" Test the various routes in for listings. """
from unittest.mock import patch, MagicMock
from flask import session
from pytest_mock import mocker
from utils.firebase import get_avg_rating


def test_login_wrapper(client):
    """
    Tests the login_wrapper decorator. This test checks that the decorator redirects to the
    login page if the user is not logged in.

    @param client - The client to use for the request
    """
    response = client.get("/favorites")

    # Check that the response is successful
    assert response.status_code == 401

    # Check that the response contains the expected content
    assert b"You must be logged in to view this page." in response.data


def test_index_route(client, mocked_posts):
    """
    Make a request to the index route and check that the response is 200.

    @param client - The client to use for the request
    @param mocked_posts - A list of mocked posts
    """
    with patch("firebase_admin.firestore.client") as firebase_mock:
        firebase_mock.return_value.collection.return_value.stream.return_value = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_posts
        ]
        # Make a request to the index route
        response = client.get("/")
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"France" in response.data
        assert b"Brussels" in response.data
    # Check that the response status code is 200


def test_my_listings_route(auth_client, mocked_posts):
    """
    Make a request to the index route and verify that it returns the correct listings.

    @param auth_client - An authenticated client to use for the test
    @param mocked_posts - A list of mocked posts
    """
    with patch("firebase_admin.firestore.client") as firebase_mock:
        firebase_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_posts
        ]
        # Make a request to the index route
        response = auth_client.get("/my-listings")
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"France" in response.data
        assert b"Paris" in response.data
    # Check that the response status code is 200


def test_my_stays_route(auth_client, mocked_posts):
    """
    Test the my_stays route.

    @param auth_client - An authenticated client to use for the test
    @param mocked_posts - A list of mocked posts
    """
    with patch("firebase_admin.firestore.client") as firebase_mock:
        mocked_rentals = [
            {
                "property": "1",
                "user_uid": "1234",
            },
            {
                "property": "2",
                "user_uid": "1234",
            },
        ]

        mocked_reviews = [
            {
                "rating": 5,
                "reviewed": "1",
                "reviewer": "1234",
            },
            {
                "rating": 4,
                "reviewed": "2",
                "reviewer": "1234",
            },
        ]
        rentals_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_rentals
        ]
        reviews_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_reviews
        ]
        posts_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_posts[:2]
        ]
        firebase_mock.return_value.collection.return_value.where.return_value.stream.side_effect = [
            rentals_mock,
            posts_mock,
            reviews_mock,
            reviews_mock,
            reviews_mock,
        ]  # you gotta call the mock as many times as you call firestore (including any nested functions and for loops)
        response = auth_client.get("/stays")
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"France" in response.data
        assert b"Paris" in response.data
        assert b"Brussels" not in response.data
        assert b"5" in response.data
        assert b"4" in response.data


# Check that the response status code is 200


def test_favs_auth(auth_client, mocked_posts, mocked_favs):
    """
    Test the favorites route while autheticated.

    @param auth_client - An authenticated client to use for the test
    @param mocked_posts - A list of mocked posts
    @param mocked_favs - A list of mocked favorites
    """
    with patch("firebase_admin.firestore.client") as firestore_mock:
        # Mock the database query to return a user's favorites
        firestore_mock.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = (
            mocked_favs
        )

        # Mock the database query to return posts for the user's favorites
        firestore_mock.return_value.collection.return_value.where.return_value.stream.return_value = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_posts
        ]

        # Make a request to the route
        response = auth_client.get("/favorites")

        # Check that the response is successful
        assert response.status_code == 200

        # Check that the response contains the expected content
        assert b"Tirana" in response.data
        assert b"Paris" in response.data
        assert b"Brussels" in response.data
        assert (
            b'class="icon ion-ios-heart"'
            or b'class="icon ion-ios-heart-outline"' not in response.data
        )
