""" Tests for the reviews blueprint. """
import unittest
from unittest.mock import patch, MagicMock, Mock
import pytest
from flask import session
from flask.testing import FlaskClient

class TestReviews(unittest.TestCase):
    """Test class for the reviews blueprint. Numbering the methods is important
    for the order of execution, because we use the side_effect parameter for the mock.
    """

    @pytest.fixture(autouse=True)
    def auth_client(self, auth_client: FlaskClient):
        """Fixture for an authenticated client available in all methods."""
        self.auth_client = auth_client

    @classmethod
    def setUpClass(cls):
        cls.mock_firestore = MagicMock()
        mocked_post = {
            "id": "1",
            "city": "Tirana",
            "country": "Albania",
            "price": 10,
        }
        mocked_review = [
            {
                "rating": "4",
                "id": "4",
                "text": "Lorem Ipsum",
                "reviewer": "1234",
                "reviewed": 1,
            }
        ]
        empty_review = []
        cls.mock_firestore.collection.return_value.where.return_value.stream.side_effect = [
            [
                MagicMock(to_dict=MagicMock(return_value=post))
                for post in [{**mocked_post, "user_uid": "123589"}]
            ],
            [
                MagicMock(to_dict=MagicMock(return_value=post))
                for post in [{**mocked_post, "user_uid": "1234"}]
            ],
            [
                MagicMock(to_dict=MagicMock(return_value=post))
                for post in [{**mocked_post, "user_uid": "12358"}]
            ],
            [MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_review],
            [MagicMock(to_dict=MagicMock(return_value=post)) for post in empty_review],
        ]
        cls.mock_firestore.collection.return_value.document.return_value.collection.return_value.where.return_value.stream.return_value = [
            Mock(to_dict=Mock(return_value=review)) for review in empty_review
        ]
        cls.mock_firestore.collection.return_value.where.return_value.where.return_value.stream.side_effect = [
            [MagicMock(to_dict=MagicMock(return_value=post)) for post in empty_review],
            [MagicMock(to_dict=MagicMock(return_value=post)) for post in mocked_review],
        ]
        cls.mock_firestore.collection.return_value.document.return_value.get.side_effect = [
            Mock(to_dict=Mock(return_value=mocked_review[0])),
            Mock(to_dict=Mock(return_value=None)),
        ]
        cls.patcher = patch(
            "firebase_admin.firestore.client", return_value=cls.mock_firestore
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_01_add_review_success(self):
        """
        Test adding a review with valid data.

        @param auth_client - An authenticated client to use for testing
        """
        response = self.auth_client.post(
            "/review/add/1", data={"rating": "4", "message": "Lorem Ipsum"}
        )
        assert response.status_code == 302
        assert response.headers["Location"] == "/stays"

        response = self.auth_client.get("/review/add/1")

        assert response.status_code == 200
        assert b'<form method="post" id="review-form"' in response.data

    def test_02_add_review_self(self):
        """
        Test adding a review to the current user's property.

        @param auth_client - An authenticated client to use for testing
        """
        response = self.auth_client.post(
            "/review/add/1", data={"rating": "4", "message": "Lorem Ipsum"}
        )
        assert response.status_code == 400
        assert b"post a review on your own property" in response.data

    def test_03_add_review_duplicate(self):
        """
        Test adding a review that already exists.

        @param auth_client - An authenticated client to use for testing
        """
        # Mock the Firestore queries
        response = self.auth_client.post(
            "/review/add/1", data={"rating": "4", "message": "Lorem Ipsum"}
        )
        # Verify that the response is a redirect
        assert response.status_code == 400
        assert b"post a review on the same property twice" in response.data

    def test_04_edit_review_post(self):
        """
        Test editing a review with valid data.

        @param auth_client - An authenticated client to use for testing
        """

        response = self.auth_client.post(
            "/review/edit/4", data={"rating": "3", "message": "Lorem Ipsum"}
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/stays"

    def test_05_edit_review_get(self):
        """
        Test the edit review form.

        @param auth_client - An authenticated client to use for testing
        """
        response = self.auth_client.get("/review/edit/4")
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert b"Lorem Ipsum</textarea" in response.data
        assert b'const valueToSelect = "4"' in response.data

    def test_06_edit_review_get_not_exist(self):
        """
        Test that editing a review that does not exist returns a 400 error.

        @param auth_client - An authenticated client to use for testing.
        """
        response = self.auth_client.get("/review/edit/4")
        assert response.status_code == 404
        assert b"Cannot edit a review that" in response.data

    def test_07_delete_review(self):
        """
        Test deleting a review.

        @param auth_client - An authenticated client to use for testing.
        """
        response = self.auth_client.get("/review/delete/4")
        assert response.status_code == 302
        assert response.headers["Location"] == "/stays"

    def test_08_delete_review_not_exist(self):
        """
        Test that delete a review that does not exist returns 400 error.

        @param auth_client - An authenticated client to use for testing.
        """
        response = self.auth_client.get("/review/delete/7")
        assert response.status_code == 400
        assert b"delete a review that doesn" in response.data
