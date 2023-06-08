""" This file contains the API endpoints for the authentication of the user. """
from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    session,
    redirect,
)

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
    session["user"] = {
        "uid": uid,
        "email": email,
        "type": typ,
        "name": name if name else "User",
        # defualt values for testing
        "verificationToken": "testing",
        "pid": "1000000000000000",
        "guests": "1000000000000000",
        "from": "1970-01-01",
        "to": "1970-01-01",
        "creation_id": "9999",
    }
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
