""" This file contains the tests for the property routes """
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest
from utils.time import convert_date


class TestPost(unittest.TestCase):
    """Test class of the various routes in the property blueprint. Numbers denote the ordering of the tests at runtime."""

    @pytest.fixture(autouse=True)
    def auth_client(self, auth_client):
        """Fixture for an authenticated client available in all methods."""
        self.auth_client = auth_client

    @pytest.fixture(autouse=True)
    def client(self, client):
        """Fixture for an unauthenticated client available in all methods."""
        self.client = client

    @classmethod
    def setUpClass(cls):
        cls.mock_firestore = MagicMock()
        ratings_data = [
            MagicMock(to_dict=MagicMock(return_value=post))
            for post in [
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
        ]
        mocked_post = [
            MagicMock(
                to_dict=lambda: {
                    "id": "1",
                    "city": "Tirana",
                    "country": "Albania",
                    "loc": "test street",
                    "district": "test district",
                    "price": 10,
                    "rating": 4,
                    "user_uid": "12358896",
                    "images": ["https://via.placeholder.com/150"],
                    "description": "This is a test description",
                    "tags": {
                        "basics": ["Wifi", "Kitchen"],
                        "safety": ["Fire extinguisher", "First aid kit"],
                        "standout": ["Pool", "Gym"],
                        "views": ["Ocean view", "Mountain view"],
                    },
                    "type": "apartment",
                    "from": convert_date("2022-01-01"),
                    "to": convert_date("2022-05-01"),
                }
            )
        ]

        cls.mock_firestore.collection.return_value.where.return_value.stream.side_effect = [
            mocked_post,
            ratings_data,
            mocked_post,
        ]

        cls.mock_firestore.collection.return_value.document.return_value = mocked_post[
            0
        ]

        cls.patcher = patch(
            "firebase_admin.firestore.client", return_value=cls.mock_firestore
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_01_view_route(self):
        """
        Tests the view route. This is a helper function to make sure that the client
        gets the correct response and returns the correct data
        """

        # Perform the request to the view route
        response = self.client.get("/view/1")

        # Assert the response status code
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"This is a test description" in response.data
        assert b"Reserve" in response.data

    @pytest.mark.skip(reason="takes too long to run")
    def test_02_get_tips(self):
        """
        Make a GET request to the tips route and verify that it returns the correct data
        """
        # Make a GET request to the route with query parameters
        response = self.client.get("/tips?city=New%20York&country=USA")

        # Assert the response status code
        assert response.status_code == 200

        print(response.get_json())

    # Test case for the route
    def test_03_delete_img(self):
        """
        Test deleting an image from Firestore. This is a test function to make sure that the delete_img route works as expected
        """
        # Create a test client using Flask's test_client() method

        # Patch the functions used in the route with the mock functions
        with patch("firebase_admin.storage.bucket"):
            # Make a GET request to the route with parameters
            response = self.auth_client.get("/delete-img/123/image.jpg")

            # Assert the response status code
            assert response.status_code == 302

            # Assert the redirect location
            assert response.headers["Location"] == "/add-6/123"

    # Test case for the route
    def test_04_delete_post_not_exist(self):
        """
        Test delete_post with not exist in Firestore. This is a test to make sure that we can't delete a post that does not exist
        """
        with patch("firebase_admin.firestore.client") as firestore:
            firestore.return_value.collection.return_value.document.return_value.get.return_value.exists = (
                None
            )
            response = self.auth_client.get("/delete/123")

            # Assert the response status code
            assert response.status_code == 404
            print(response.data.decode("utf-8"))
            assert b"delete a post that does not" in response.data

    # Test case for the route
    def test_05_delete_post(self):
        """
        Test a DELETE request with a post that is mocked. This is a test to make sure that we can delete a post that exists
        """
        response = self.auth_client.get("/delete/1")

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
