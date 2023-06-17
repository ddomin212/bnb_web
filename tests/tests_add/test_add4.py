from unittest.mock import patch, MagicMock


def test_add_4_get(auth_client):
    # Make a GET request to the route with parameters
    response = auth_client.get("/add-4")

    # Assert the response status code
    assert response.status_code == 200
    assert b"<fieldset multiple>" in response.data


def test_add_4_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-4",
            data={
                "basics": ["Paid parking", "Free parking", "Kitchen"],
                "safety": ["Smoke alarm", "CO detector", "First aid kit"],
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/add-5"


def test_add_4_edit_get(auth_client, mocked_posts):
    with patch("firebase_admin.firestore.client") as firestore:
        firestore.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
            to_dict=lambda: mocked_posts[0]
        )
        # Make a GET request to the route with parameters
        response = auth_client.get("/add-4/1")

        # Assert the response status code
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert b'<input type="checkbox"' in response.data


def test_add_4_edit_post(auth_client):
    # Make a GET request to the route with parameters
    with patch("firebase_admin.firestore.client"):
        response = auth_client.post(
            "/add-4/1",
            data={
                "basics": ["Paid parking", "Free parking", "Kitchen"],
                "safety": ["Smoke alarm", "CO detector", "First aid kit"],
            },
        )

        # Assert the response status code
        assert response.status_code == 302
        assert response.headers["Location"] == "/edit/1"
