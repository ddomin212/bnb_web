from unittest.mock import patch, MagicMock


def test_add_7_get(auth_client):
    # Make a GET request to the route with parameters
    response = auth_client.get("/add-7")

    # Assert the response status code
    assert response.status_code == 200
    assert (
        b'<input class="form-control-sm form-control w-50" name="bedrooms"'
        in response.data
    )


def test_add_7_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-7",
            data={
                "bedrooms": "1",
                "baths": "1",
                "guests": "1",
                "beds": "1",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/add-8"


def test_add_7_edit_get(auth_client, mocked_posts):
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/add-7/1")

        # Assert the response status code
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert (
            b'<input class="form-control-sm form-control w-50" name="bedrooms" type="number" value="1"'
            in response.data
        )


def test_add_7_edit_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-7/1",
            data={
                "bedrooms": "1",
                "baths": "1",
                "guests": "1",
                "beds": "1",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"
