""" Tests for the favorites blueprint. """
import unittest
from unittest.mock import patch, MagicMock
import pytest
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from flask.testing import FlaskClient

class TestFavs(unittest.TestCase):
    """Test class for the favorites blueprint. Default alphabetical ordering of tests at runtime will do in this case."""

    @pytest.fixture(autouse=True)
    def auth_client(self, auth_client: FlaskClient):
        """Fixture for an authenticated client available in all methods."""
        self.auth_client = auth_client

    @classmethod
    def setUpClass(cls):
        cls.mock_firestore = MagicMock()
        mocked_favs = [
            {"favs": ["4"]},
            None,
            {"favs": ["4", "5"]},
            {"favs": ["4", "5"]},
        ]
        cls.mock_firestore.collection.return_value.document.return_value.get.side_effect = [
            MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_favs
        ]
        cls.patcher = patch(
            "firebase_admin.firestore.client", return_value=cls.mock_firestore
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_add_fav_exists(self):
        """
        Test that adding a favorite that already exists returns 400.

        """
        response = self.auth_client.get("/fav/add/4")
        assert response.status_code == 400
        assert response.data == b"Bad request"

    def test_add_fav_success(self):
        """
        Test that adding a favorite works as expected.

        """
        response = self.auth_client.get("/fav/add/4")
        assert response.status_code == 200
        assert response.data == b"Success"

    def test_delete_fav(self):
        """
        Test deleting a favorite.

        """
        response = self.auth_client.get("/fav/delete/5")
        assert response.status_code == 200
        assert response.data == b"Success"

    def test_delete_fav_not_found(self):
        """
        Test deleting a favorite that does not exist. Should return 404.

        """
        response = self.auth_client.get("/fav/delete/7")
        assert response.status_code == 404
        assert response.data == b"Favorite not found"
