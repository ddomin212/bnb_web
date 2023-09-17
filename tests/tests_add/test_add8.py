from unittest.mock import patch, MagicMock


def test_add_8_get(auth_client):
    """
    Test the page for the property pricing.

    @param auth_client - The client to make requests to the server
    """
    response = auth_client.get("/add-8")

    # Assert the response status code
    assert response.status_code == 200
    assert b'name="price" type="number"' in response.data


def test_add_8_post(auth_client):
    """
    Test the form for the property pricing.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-8",
            data={
                "price": "100",
                "month-disc": "15",
                "year-disc": "20",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/9999"


def test_add_8_edit_get(auth_client, mocked_posts):
    """
    Test the edit page for a property location.

    @param auth_client - The client to make requests to the server
    @param mocked_posts - The mocked posts to return from the database
    """
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        response = auth_client.get("/add-8/1")

        # Assert the response status code
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert (
            b'<input class="form-control-sm form-control w-75" value="15" name="month-disc"'
            in response.data
        )
        assert (
            b'<input class="form-control-sm form-control w-75" value="20" name="year-disc"'
            in response.data
        )
        assert (
            b'<input class="form-control-sm form-control w-75" value="10" name="price"'
            in response.data
        )


def test_add_8_edit_post(auth_client):
    """
    Test the edit form for the property pricing.

    @param auth_client - The client to make requests to the server
    """
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-8/1",
            data={
                "price": "100",
                "month-disc": "15",
                "year-disc": "20",
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/9999"
