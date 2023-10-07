from flask import render_template
from google.cloud.exceptions import GoogleCloudError
from functools import wraps

def error_handler(func: callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GoogleCloudError:
            return render_message(500, "Cannot connect to database")
        except RuntimeError:
            return render_message(404, "No items found")
        except Exception:
            return render_message(500, "Internal server error")
    return wrapper

def render_message(code: int, message: str):
    return (
        render_template(
            "message.html", error_message=message, status_code=code
        ),
        code,
    )
