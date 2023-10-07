""" Test the various routes in for listings. """
import unittest
from unittest.mock import patch, MagicMock
import pytest
from utils.time import convert_date


class TestMain(unittest.TestCase):
    """Test class for the favorites blueprint. Numbers denote the ordering of the tests at runtime."""

    @pytest.fixture(autouse=True)
    def client(self, client):
        """Fixture for an unauthenticated client available in all methods."""
        self.client = client

    @pytest.fixture(autouse=True)
    def auth_client(self, auth_client):
        """Fixture for an authenticated client available in all methods."""
        self.auth_client = auth_client

    @classmethod
    def setUpClass(cls):
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
            {
                "id": "3",
                "city": "Brussels",
                "country": "Belgium",
                "price": 30,
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
        posts_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_posts
        ]
        rentals_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_rentals
        ]
        reviews_mock = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_reviews
        ]
        cls.mock_firestore.collection.return_value.stream.return_value = posts_mock
        cls.mock_firestore.collection.return_value.where.return_value.stream.side_effect = [
            posts_mock,
            rentals_mock,
            posts_mock,
            reviews_mock,
            posts_mock,
        ]
        cls.mock_firestore.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            "favs": ["1", "2", "3"]
        }
        cls.patcher = patch(
            "firebase_admin.firestore.client", return_value=cls.mock_firestore
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    @patch("components.firebase.database.get_avg_rating", return_value=4.5)
    def test_01_index(self, mock_get_avg_rating):
        """
        Make a request to the index route and check that the response is 200.

        @param client - The client to use for the request
        @param mocked_posts - A list of mocked posts
        """
        response = self.client.get("/")
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"France" in response.data
        assert b"Brussels" in response.data

    @patch("components.firebase.database.get_avg_rating", return_value=4.5)
    def test_02_my_listings(self, mock_get_avg_rating):
        """
        Make a request to the index route and verify that it returns the correct listings.

        @param auth_client - An authenticated client to use for the test
        @param mocked_posts - A list of mocked posts
        """
        response = self.auth_client.get("/my-listings")
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"France" in response.data
        assert b"Paris" in response.data

    @patch("components.firebase.database.get_avg_rating", return_value=4.5)
    def test_03_my_stays(self, mock_get_avg_rating):
        """
        Test the my_stays route.

        @param auth_client - An authenticated client to use for the test
        @param mocked_posts - A list of mocked posts
        """
        response = self.auth_client.get("/stays")
        assert response.status_code == 200
        assert b"Tirana" in response.data
        assert b"France" in response.data
        assert b"Paris" in response.data
        assert b"5" in response.data
        assert b"4" in response.data

    @patch("components.firebase.database.get_avg_rating", return_value=4.5)
    def test_04_favs(self, mock_get_avg_rating):
        """
        Test the favorites route while autheticated.

        @param auth_client - An authenticated client to use for the test
        @param mocked_posts - A list of mocked posts
        @param mocked_favs - A list of mocked favorites
        """
        # Make a request to the route
        response = self.auth_client.get("/favorites")

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
