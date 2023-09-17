"""
Handles user authentication for Flask routes.

This module contains a decorator 
function for checking if the user is logged in.

Functions:
    login_required: A decorator function that checks if the user is logged in.
"""

from functools import wraps

from flask import render_template, session


def login_required(f):
    """
    A decorator function that checks if the user is logged in before allowing access
    to a Flask route. If the user is not logged in, returns a 401 Unauthorized error.

    Args:
        f (function): The Flask route function to decorate.

    Returns:
        function: The decorated Flask route function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return (
                render_template(
                    "message.html",
                    error_message="You must be logged in to view this page.",
                    status_code=401,
                ),
                401,
            )
        return f(*args, **kwargs)

    return decorated_function


def set_user_session(uid, email, typ, name=None):
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
