from unittest.mock import patch, MagicMock


def test_add_2_get(auth_client):
    """
    Test the page for a property availability and type.

    @param auth_client - The client to make requests to the server
    """
    response = auth_client.get("/add-2")

    # Assert the response status code
    assert response.status_code == 200
    assert b"<input" in response.data


def test_add_2_post(auth_client):
    """
    Test the form for a property availability and type.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-2",
            data={
                "type": "apartment",
                "from": "2022-01-01",
                "to": "2022-01-31",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/add-3"


def test_add_2_edit_get(auth_client, mocked_posts):
    """
    Test the edit page for a property availability and type.

    @param auth_client - The client to make requests to the server
    @param mocked_posts - The mocked posts to return from the database
    """
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        response = auth_client.get("/add-2/1")

        # Assert the response status code
        assert response.status_code == 200
        assert b'<option value="apartment" selected=""' in response.data


def test_add_2_edit_post(auth_client):
    """
    Test the edit form for a property availability and type.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-2/1",
            data={
                "type": "apartment",
                "from": "2022-01-01",
                "to": "2022-01-31",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"
