""" Test authentication functionality. """
import unittest
import pytest
from flask import session


class TestAuth(unittest.TestCase):
    """Test class for the authentication functionality. Default alphabetical ordering of tests at runtime will do in this case."""

    @pytest.fixture(autouse=True)
    def client(self, client):
        """Fixture for an unauthenticated client available in all methods."""
        self.client = client

    @pytest.fixture(autouse=True)
    def auth_client(self, auth_client):
        """Fixture for an authenticated client available in all methods."""
        self.auth_client = auth_client

    def test_login_success(self):
        """
        Test successful login to API.

        @param client - the fixture of a client to use
        """
        with self.client:
            response = self.client.post(
                "/api/login",
                json={
                    "name": "John",
                    "password": "secret",
                    "email": "john@example.com",
                    "type": "user",
                },
            )
            assert "user" in session
            assert session["user"]["name"] == "John"
            assert session["user"]["email"] == "john@example.com"
        assert response.status_code == 200
        assert response.json == {"message": "login succeded"}

    def test_login_wrapper(self):
        """
        Tests the login_wrapper decorator. This test checks that the decorator redirects to the
        login page if the user is not logged in.

        @param client - The client to use for the request
        """
        response = self.client.get("/favorites")

        # Check that the response is successful
        assert response.status_code == 401

        # Check that the response contains the expected content
        assert b"You must be logged in to view this page." in response.data

    def test_login_failure(self):
        """
        Test that login fails if there are missing data.

        @param client - the fixture of a client to use
        """
        response = self.client.post(
            "/api/login", json={"name": "John", "email": "john@example.com"}
        )
        assert response.status_code == 400
        assert response.json == {"message": "missing some request data"}

    def test_login(self):
        """
        Test login page.

        @param client - the fixture of a client to use
        """
        response = self.client.get("/login")
        assert response.status_code == 200
        assert b"<h2>Log in with...</h2>" in response.data

    def test_logout(self):
        """
        Test logout of user.

        @param auth_client - the fixture of an authenticated client to use
        """
        response = self.auth_client.get("/logout")
        assert "user" not in session
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
