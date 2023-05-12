from flask import session


def test_api_login_missing_some_data(client):
    response = client.post(
        '/api/login', json={"name": "John", "email": "john@example.com"})
    assert response.status_code == 400
    assert response.json == {"message": "missing some request data"}


def test_api_login_success(client):
    with client:
        response = client.post(
            '/api/login', json={"name": "John", "password": "secret", "email": "john@example.com", "type": "user"})
        assert 'user' in session
        assert session["user"]["name"] == "John"
        assert session["user"]["email"] == "john@example.com"
    assert response.status_code == 200
    assert response.json == {"message": "login succeded"}


def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<h2>Log in with...</h2>' in response.data


def test_logout(auth_client):
    response = auth_client.get(
        '/logout')
    assert 'user' not in session
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

#!! TODO: Add tests for session['user'] and session['user']['type'].
