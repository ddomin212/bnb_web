from unittest.mock import patch, MagicMock


def test_add_1_edit_get(auth_client, mocked_posts):
    """
    Test the edit page for a property location.

    @param auth_client - The client to make requests to the server
    @param mocked_posts - The mocked posts to return from the database
    """
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/add-1/1")

        # Assert the response status code
        assert response.status_code == 200
        assert b"Tirana" in response.data


def test_add_1_get(auth_client):
    """
    Test the page for a property location.

    @param auth_client - The client to make requests to the server
    """
    # Make a GET request to the route with parameters
    response = auth_client.get("/add-1")

    # Assert the response status code
    assert response.status_code == 200
    assert b"<input" in response.data


def test_add_1_edit_post(auth_client):
    """
    Test editing the form for a property location.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-1/1",
            data={
                "address_line": "Taborska 987, 29301 Mlada Boleslav, Czechia",
                "address_line2": "third floor",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"


def test_add_1_post(auth_client):
    """
    Test the form for a property location.

    @param auth_client - The client to make requests to the server
    """
    response = auth_client.post(
        "/add-1",
        data={
            "address_line": "Taborska 987, 29301 Mlada Boleslav, Czechia",
            "address_line2": "third floor",
        },
    )

    # Assert the response status code
    assert response.status_code == 302
    assert response.headers["Location"] == "/add-2"
