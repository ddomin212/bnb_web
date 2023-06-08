""" This module contains tests for the profile view. """
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest
from flask import session
from utils.time import convert_date


class TestProfile(unittest.TestCase):
    """Test class for the profile view. Default alphabetical ordering of tests at runtime will do in this case."""

    @pytest.fixture(autouse=True)
    def auth_client(self, auth_client):
        """Fixture for an authenticated client available in all methods."""
        self.auth_client = auth_client

    @classmethod
    def setUpClass(cls):
        cls.phone = "555-555-5555"
        cls.description = "This is a test description"
        cls.uid = "1234"
        cls.mock_firestore = MagicMock()
        mocked_posts = [
            {
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
            },
            {
                "id": "2",
                "city": "Paris",
                "country": "France",
                "price": 20,
                "rating": 4,
                "user_uid": "1234",
                "images": ["https://via.placeholder.com/150"],
                "tags": {
                    "basics": ["Wifi", "Kitchen"],
                    "safety": ["Fire extinguisher", "First aid kit"],
                    "standout": ["Pool", "Gym"],
                    "views": ["Ocean view", "Mountain view"],
                },
            },
        ]

        mocked_reviews = [
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
        posts_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_posts
        ]
        reviews_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_reviews
        ]
        cls.mock_firestore.collection.return_value.where.return_value.stream.side_effect = [
            posts_mock,
            posts_mock,
            reviews_mock,
        ]
        cls.patcher = patch(
            "firebase_admin.firestore.client", return_value=cls.mock_firestore
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_add_description(self):
        """
        Test adding a description to the user's profile page.

        @param auth_client - An authenticated client to use for the test
        """
        # Set up test data

        # Set up expected data
        expected_data = {"phone": self.phone, "description": self.description[:1000]}

        # Mock the Firebase admin auth module
        with patch("firebase_admin.auth.set_custom_user_claims") as mock_set_claims:
            # Make a request to the Flask route
            response = self.auth_client.post(
                "/user/add-info",
                data={"phone": self.phone, "description": self.description},
            )

            # Assert that the response is a redirect to the user's profile page
            assert response.status_code == 302
            assert response.headers["Location"] == f"/user/{self.uid}"

            # Assert that the mock function was called with the expected data
            mock_set_claims.assert_called_once_with(self.uid, expected_data)

    @patch("utils.firebase.get_avg_rating", return_value=4.5)
    def test_view_user(self, mock_get_avg_rating):
        """
        Test the view_user method. This is a test for the rating_view. py script.

        @param client - An authenticated client to use for the test
        @param mocked_posts - A list of mocked posts
        """
        # Set up test data
        user_data = {
            "display_name": "Test User",
            "email": "testuser@example.com",
            "uid": self.uid,
            "photo_url": "https://example.com/photo.jpg",
        }
        user = MagicMock()
        user.custom_claims = {
            "description": self.description,
            "phone": self.phone,
        }
        user.display_name = user_data["display_name"]
        user.email = user_data["email"]
        user.uid = user_data["uid"]
        user.photo_url = user_data["photo_url"]

        # Mock the Firebase admin auth module and the database fetch function
        with patch("firebase_admin.auth.get_user") as mock_get_user:
            mock_get_user.return_value = user
            # Make a request to the Flask route
            response = self.auth_client.get(f"/user/{self.uid}")

            # Assert that the response is a success and that the correct data is in the response context
            assert response.status_code == 200
            print(response.data.decode("utf-8"))
            assert b"Test User" in response.data
            assert b"This is a test description" in response.data
            assert b"555-555-5555" in response.data
            assert b"Paris" in response.data
