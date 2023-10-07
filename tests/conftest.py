""" The pytest configuration file. This file is used to configure pytest and create fixtures that can be used in tests. """
from unittest.mock import MagicMock
import pytest
from utils.time import convert_date
from flask import Flask

@pytest.fixture()
def app():
    """
    Fixture for Flask app. This fixture is used to create a Flask app in test mode.
    """
    from app import create_app

    app = create_app(testing=True)
    yield app


@pytest.fixture()
def client(app: Flask):
    """
    Create a test client for the given app. This is a convenience function to use in tests that need to test the client.

    @param app - The Flask application to test. Must be a : class : ` werkzeug. Flask ` instance.

    @return A : class : ` werkzeug. TestClient ` instance that can be used to make requests
    """
    return app.test_client()


@pytest.fixture()
def auth_client(app: Flask):
    """
    Fixture for authentificated client. This fixture is used to test authentificatied routes.

    @param app - The Flask application instance to test the client with
    """
    with app.test_client() as client:
        client.post(
            "/api/login",
            json={
                "name": "John",
                "password": "1234",
                "email": "john@example.com",
                "type": "user",
            },
        )
        yield client


@pytest.fixture()
def mocked_posts():
    """
    Returns a list of mocked posts. This is useful for testing the post creation and post update functions.


    @return A list of post dictionaries that would be returned by the database.
    """
    return [
        {
            "id": "1",
            "city": "Tirana",
            "country": "Albania",
            "loc": "test street",
            "district": "test district",
            "price": 10,
            "rating": 4,
            "user_uid": "12358896",
            "images": [
                "https://via.placeholder.com/150",
                "https://via.placeholder.com/300",
                "https://via.placeholder.com/450",
            ],
            "description": "This is a test description",
            "tags": {
                "basics": '["Wifi", "Kitchen"]',
                "safety": '["Fire extinguisher", "First aid kit"]',
                "standout": '["Pool", "Gym"]',
                "views": '["Ocean view", "Mountain view"]',
            },
            "type": "apartment",
            "bedrooms": "1",
            "bathrooms": "1",
            "guests": "1",
            "beds": "1",
            "month_disc": "15",
            "year_disc": "20",
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


@pytest.fixture(scope="class")
def mocked_favs():
    """
    Mock a dictionary of favs. This is used to test the favorites.


    @return A dictionary of favs that would be returned by the database.
    """
    return {"favs": ["1", "2", "3"]}


@pytest.fixture()
def firebase_client(mocker):
    """
    Mock firebase client. This is a helper function to make tests easier.
    It patches the firebase client with a mock.

    @param mocker - The Mocker to patch the client with.

    @return The mocked firebase client for use in tests that require it ( not a fixture )
    """
    client = MagicMock()
    mocker.patch("firebase_admin.firestore.client", return_value=client)
    return client


# TODO! Create tests in class format. This is a better way to organize tests.
