from flask import render_template


def render_message(code, message):
    return (
        render_template(
            "message.html", error_message=message, status_code=code
        ),
        code,
    )
