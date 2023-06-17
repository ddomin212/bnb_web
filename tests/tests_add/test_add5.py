from unittest.mock import patch, MagicMock


def test_add_5_get(auth_client):
    # Make a GET request to the route with parameters
    response = auth_client.get("/add-5")

    # Assert the response status code
    assert response.status_code == 200
    assert b"<textarea" in response.data


def test_add_5_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-5",
            data={"desc": "This is a test description22"},
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/add-6"


def test_add_5_edit_get(auth_client, mocked_posts):
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/add-5/1")

        # Assert the response status code
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert (
            b'<textarea name="desc" style="max-width: 1000px;min-width: 400px;" rows="20">This is a test description'
            in response.data
        )


def test_add_5_edit_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-5/1",
            data={"desc": "This is a test description22"},
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"
