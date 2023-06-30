""" This file contains the API endpoints for the authentication of the user. """
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
)

from utils.auth import set_user_session

authapi = Blueprint("authapi", __name__)


@authapi.route("/login")
def login():
    """
    Login page for the app.


    @return The template to render for the login page.`
    """
    return render_template("auth.html", hidenav=True)


@authapi.route("/api/login", methods=["POST"])
def api_login():
    """
    Log the user into app. This will set the session cookie for the user and will allow them
    to access the full features of the app.


    @return 200 if successful 400 if not.
    """
    try:
        name = request.json["name"]
        uid = request.json["password"]
        email = request.json["email"]
        typ = request.json["type"]
    except KeyError:
        return jsonify({"message": "missing some request data"}), 400
    set_user_session(uid, email, typ, name)
    return jsonify({"message": "login succeded"}), 200


@authapi.route("/logout")
def logout():
    """
    Log out the currently logged in user. This will remove the session cookie for the
    user and will prevent them from accessing the full features of the app.


    @return 200 if successful 400 if not.
    """
    try:
        session.pop("user")
        return redirect("/")
    except KeyError:
        return jsonify({"message": "no user logged in"}), 400
