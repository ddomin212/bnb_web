from unittest.mock import patch, MagicMock


def test_add_3_get(auth_client):
    # Make a GET request to the route with parameters
    response = auth_client.get("/add-3")

    # Assert the response status code
    assert response.status_code == 200
    assert b"<input" in response.data


def test_add_3_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-3",
            data={"space": "whole"},
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/add-4"


def test_add_3_edit_get(auth_client, mocked_posts):
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/add-3/1")

        # Assert the response status code
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert (
            b'<input name="space" type="radio" class="form-check-input mt-0"'
            in response.data
        )


def test_add_3_edit_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-3/1",
            data={"space": "whole"},
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"
