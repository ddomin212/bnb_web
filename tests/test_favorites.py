from unittest.mock import patch, Mock
from google.cloud.firestore_v1 import SERVER_TIMESTAMP


def test_add_fav_success(auth_client):
    with patch('firebase_admin.firestore.client') as mock_fetch_db:
        mock_firestore = Mock()
        mock_firestore.collection.return_value.document.return_value.get.return_value.to_dict.return_value = None
        mock_fetch_db.return_value = mock_firestore
        response = auth_client.get('/fav/add/4')
        assert response.status_code == 200
        assert response.data == b'Success'


def test_add_fav_already_exists(auth_client):
    with patch('firebase_admin.firestore.client') as mock_fetch_db:
        mock_firestore = Mock()
        mock_firestore.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'favs': ['4'], 'timestamp': SERVER_TIMESTAMP}
        mock_fetch_db.return_value = mock_firestore
        response = auth_client.get('/fav/add/4')
        assert response.status_code == 400
        assert response.data == b'Bad request'


def test_delete_fav(auth_client):
    with patch('firebase_admin.firestore.client') as mock_fetch_db:
        mock_firestore = Mock()
        mock_firestore.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'favs': ['4', '5']
        }
        mock_fetch_db.return_value = mock_firestore

        response = auth_client.get('/fav/delete/5')
        assert response.status_code == 200
        assert response.data == b'Success'


def test_delete_fav_not_found(auth_client):
    with patch('firebase_admin.firestore.client') as mock_fetch_db:
        mock_firestore = Mock()
        mock_firestore.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            'favs': ['4', '5']
        }
        mock_fetch_db.return_value = mock_firestore

        response = auth_client.get('/fav/delete/7')
        assert response.status_code == 404
        assert response.data == b'Favorite not found'
