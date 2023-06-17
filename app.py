""" The main entry point for the Flask application. """
import os
from flask import Flask
from dotenv import load_dotenv
from views import main, authapi, posts, reviews, profile, payments, add, fav
from config import initialize_app


def create_app(testing=False):
    """
    Create and return a Flask application. This is a factory method to create a : class : ` Flask `
    application and register all blueprints in the application

    @return Flask application ready to be used.
    """
    # Load dotenv if not production
    if os.getenv("FLASK_ENV") != "production":
        load_dotenv()
    app = Flask(__name__)

    initialize_app(app, testing=testing)

    app.register_blueprint(main)
    app.register_blueprint(authapi)
    app.register_blueprint(posts)
    app.register_blueprint(reviews)
    app.register_blueprint(profile)
    app.register_blueprint(payments)
    app.register_blueprint(add)
    app.register_blueprint(fav)
    return app


app = create_app()


# Run the app if __main__ is not the main module.
if __name__ == "__main__":
    app.run(debug=True)
