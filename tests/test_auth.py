""" Test authentication functionality. """
from flask import session


def test_api_login_missing_some_data(client):
    """
    Test that login fails if there are missing data.

    @param client - the fixture of a client to use
    """
    response = client.post(
        "/api/login", json={"name": "John", "email": "john@example.com"}
    )
    assert response.status_code == 400
    assert response.json == {"message": "missing some request data"}


def test_api_login_success(client):
    """
    Test successful login to API.

    @param client - the fixture of a client to use
    """
    with client:
        response = client.post(
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


def test_login(client):
    """
    Test login page.

    @param client - the fixture of a client to use
    """
    response = client.get("/login")
    assert response.status_code == 200
    assert b"<h2>Log in with...</h2>" in response.data


def test_logout(auth_client):
    """
    Test logout of user.

    @param auth_client - the fixture of an authenticated client to use
    """
    response = auth_client.get("/logout")
    assert "user" not in session
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
