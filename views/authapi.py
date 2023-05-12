from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for,
)
import json

authapi = Blueprint("authapi", __name__)


@authapi.route("/login")
def login():
    return render_template("auth.html", hidenav=True)


@authapi.route("/api/login", methods=["POST"])
def api_login():
    try:
        name = request.json["name"]
        uid = request.json["password"]
        email = request.json["email"]
        type = request.json["type"]
    except KeyError:
        return jsonify({"message": "missing some request data"}), 400
    session["user"] = {
        "uid": uid,
        "email": email,
        "type": type,
        "name": name if name else "User",
        "verificationToken": "testing",
    }
    return jsonify({"message": "login succeded"}), 200


@authapi.route("/logout")
def logout():
    try:
        session.pop("user")
        return redirect("/")
    except KeyError:
        return jsonify({"message": "no user logged in"}), 400
