
from flask import Blueprint, render_template, redirect, request, session, jsonify
from utils.firebase import get_avg_rating, update_favorites, add_favorite
from config import fetch_db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from utils.auth import login_required

fav = Blueprint('fav', __name__)


@fav.route('/fav/add/<pid>', methods=['GET'])
@login_required
def add_fav(pid):
    fav_doc = fetch_db().collection('fav').document(
        session['user']['uid']).get().to_dict()
    print(fav_doc)
    if fav_doc:
        if pid in fav_doc['favs']:
            return "Bad request", 400
        data = {
            "favs": fav_doc['favs'] + [pid],
            "timestamp": SERVER_TIMESTAMP
        }
        update_favorites(data)
        return "Success", 200
    else:
        data = {
            "favs": [pid],
            "timestamp": SERVER_TIMESTAMP
        }
        add_favorite(data)
        return "Success", 200


@fav.route('/fav/delete/<pid>', methods=['GET'])
@login_required
def delete_fav(pid):
    fav_doc = fetch_db().collection('fav').document(
        session['user']['uid']).get().to_dict()
    found = False
    for idx, e in enumerate(fav_doc['favs']):
        if e == str(pid):
            fav_doc['favs'].pop(idx)
            found = True
            break
    if found == False:
        return "Favorite not found", 404
    data = {
        "favs": fav_doc['favs'],
        "timestamp": SERVER_TIMESTAMP
    }
    update_favorites(data)
    return "Success", 200
