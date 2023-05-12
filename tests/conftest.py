import pytest
from flask import session
from unittest.mock import MagicMock
from pytest_mock import mocker


@pytest.fixture()
def app():
    from app import create_app

    app = create_app(testing=True)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(app):
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
            "images": ["https://via.placeholder.com/150"],
            "description": "This is a test description",
            "tags": {
                "basics": ["Wifi", "Kitchen"],
                "safety": ["Fire extinguisher", "First aid kit"],
                "standout": ["Pool", "Gym"],
                "views": ["Ocean view", "Mountain view"],
            },
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


@pytest.fixture()
def mocked_favs():
    return {"favs": ["1", "2", "3"]}


@pytest.fixture()
def firebase_client(mocker):
    client = MagicMock()
    mocker.patch("firebase_admin.firestore.client", return_value=client)
    return client
