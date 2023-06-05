import os
from flask import Flask
from views import *
from config import initialize_extensions
from dotenv import load_dotenv


def create_app():
    """
    Create and return a Flask application. This is a factory method to create a : class : ` Flask `
    application and register all blueprints in the application

    @return Flask application ready to be used.
    """
    # Load dotenv if not production
    if os.getenv("FLASK_ENV") != "production":
        load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("PAGE_SECRET_KEY")
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    initialize_extensions(app, testing=testing)

    @app.context_processor
    def inject_variables():
        """
        Inject variables into command line. This is useful for testing the execution environment.
        The environment will be injected as a dictionary with the key " env "
        and the value being the value of the environment variables.


        @return dictionary with the environment variables to inject into the command line.
        """
        return {"env": os.environ}

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
