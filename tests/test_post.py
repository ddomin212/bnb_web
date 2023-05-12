from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest


def test_view_route(client, monkeypatch, mocked_posts):
    with patch("firebase_admin.firestore.client") as mock_db:
        ratings_data = [
            {
                "rating": 5,
                "reviewed": "1",
                "reviewer": "1234",
                "timestamp": datetime.now(),
            },
            {
                "rating": 4,
                "reviewed": "2",
                "reviewer": "1234",
                "timestamp": datetime.now(),
            },
        ]

        mock_db.return_value.collection.return_value.where.return_value.stream.side_effect = [
            [MagicMock(to_dict=lambda: mocked_posts[0])],
            [MagicMock(to_dict=lambda: data) for data in ratings_data],
        ]

        # Perform the request to the view route
        response = client.get("/view/1")

        # Assert the response status code
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"This is a test description" in response.data
        assert b"Reserve" in response.data


@pytest.mark.skip(reason="takes too long to run")
def test_get_tips(client):
    # Make a GET request to the route with query parameters
    response = client.get("/tips?city=New%20York&country=USA")

    # Assert the response status code
    assert response.status_code == 200

    print(response.get_json())


# Test case for the route
def test_delete_img(auth_client, mocked_posts):
    # Create a test client using Flask's test_client() method

    # Patch the functions used in the route with the mock functions
    with patch("firebase_admin.firestore.client") as firestore, patch(
        "firebase_admin.storage.bucket"
    ) as fb_bucket:
        firestore.return_value.collection.return_value.where.return_value.stream.return_value = [
            MagicMock(to_dict=lambda: mocked_posts[0])
        ]
        # Make a GET request to the route with parameters
        response = auth_client.get("/delete-img/123/image.jpg")

        # Assert the response status code
        assert response.status_code == 302

        # Assert the redirect location
        assert response.headers["Location"] == "/add-6/123"


# Test case for the route
def test_delete_post_not_exist(auth_client, mocked_posts):
    # Create a test client using Flask's test_client() method

    # Patch the functions used in the route with the mock functions
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value.exists = (
            None
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/delete/123")

        # Assert the response status code
        assert response.status_code == 404
        print(response.data.decode("utf-8"))
        assert b"delete a post that does not" in response.data


# Test case for the route
def test_delete_post(auth_client, mocked_posts):
    # Create a test client using Flask's test_client() method

    # Patch the functions used in the route with the mock functions
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value = (
            MagicMock(to_dict=lambda: mocked_posts[0])
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/delete/1")

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
