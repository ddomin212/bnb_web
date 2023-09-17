from unittest.mock import patch, MagicMock


def test_add_6_get(auth_client):
    """
    Test the page for the property images.

    @param auth_client - The client to make requests to the server
    """
    response = auth_client.get("/add-6")

    # Assert the response status code
    assert response.status_code == 200
    assert b'<i class="fa fa-upload d-block p-4"' in response.data


def test_add_6_post(auth_client):
    """
    Test the form for the property images.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-6",
            data={"images": ["https://via.placeholder.com/550"]},
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/add-7"


def test_add_6_edit_get(auth_client, mocked_posts):
    """
    Test the edit page for the property images.

    @param auth_client - The client to make requests to the server
    @param mocked_posts - The mocked posts to return from the database
    """
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )

        response = auth_client.get("/add-6/1")

        # Assert the response status code
        assert response.status_code == 200
        assert b'<img src="https://via.placeholder.com/150"' in response.data
        assert b'<img src="https://via.placeholder.com/300"' in response.data
        assert b'<img src="https://via.placeholder.com/450"' in response.data


def test_add_6_edit_post(auth_client):
    """
    Test the edit form for the property images.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-6/1",
            data={"images": ["https://via.placeholder.com/550"]},
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"
