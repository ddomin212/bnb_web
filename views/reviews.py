from flask import Blueprint, render_template, redirect, request, session, jsonify
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from utils.firebase import add_to_firestore, update_firestore
from config import fetch_db
import json

reviews = Blueprint('reviews', __name__)


@reviews.route('/review/add/<pid>', methods=['GET', 'POST'])
def add_review(pid):
    if request.method == 'POST':
        self_review = fetch_db().collection('posts').where("id", "==", int(pid)).stream()
        try:
            doc = [doc.to_dict() for doc in self_review][0]
        except IndexError:
            return render_template("message.html", error_message="Cannot check for duplicate (no posts)", status_code=404), 404
        if doc["user_uid"] == session["user"]["uid"]:
            return render_template("message.html", error_message="You can't post a review on your own property", status_code=400), 400
        duplicate = fetch_db().collection('reviews').where("reviewed", "==", int(pid)
                                                           ).where("reviewer", "==", session['user']['uid']).stream()
        duplicates = [doc.to_dict() for doc in duplicate]
        if len(duplicates) > 0:
            return render_template("message.html", error_message="You can't post a review on the same property twice", status_code=400), 400

        data = {
            "rating": int(request.form['rating']),
            "text": request.form['message'],
            "reviewer": session['user']['uid'],
            "displayName": session['user']['name'],
            "reviewed": int(pid),
            "timestamp": SERVER_TIMESTAMP
        }
        add_to_firestore(data, 'reviews')
        return redirect('/stays')
    else:
        return render_template('review.html')


@reviews.route('/review/edit/<id>', methods=['GET', 'POST'])
def edit_review(id):
    if request.method == 'POST':
        data = {
            "rating": int(request.form['rating']),
            "text": request.form['message'],
            "timestamp": SERVER_TIMESTAMP
        }
        update_firestore(data, id, 'reviews')
        return redirect('/stays')
    else:
        history = fetch_db().collection('reviews').where("id", "==", int(id)).stream()
        try:
            doc = [doc.to_dict() for doc in history][0]
        except IndexError:
            return render_template("message.html", error_message="Cannot edit a review that doesn't exist", status_code=400), 400
        return render_template('review.html', doc=doc)


@reviews.route('/review/delete/<id>', methods=['GET'])
def delete_review(id):
    doc_ref = fetch_db().collection('reviews').document(
        f'{id}|{session["user"]["uid"]}')
    if doc_ref.get().to_dict() == None:
        return render_template("message.html", error_message="You can't delete a review that doesn't exist", status_code=400), 400
    doc_ref.delete()
    return redirect('/stays')
