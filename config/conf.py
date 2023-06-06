""" Configures the app and registers all blueprints. """
import os
import stripe
from .firebase import initialize_firebase
from .redis import initialize_redis


def initialize_app(app, testing=False):
    """
    Initialize app enviroment and extensions, such as redis and firebase.
    This function should be called before running the app.

    @param app - The Flask application instance. This should be passed as the first argument to this function
    @param testing - If True this we are testing the application. This will prevent the initialization of redis and firebase.
    """
    # Initialize redis and firebase if not testing
    app.secret_key = os.getenv("PAGE_SECRET_KEY")
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    stripe.api_key = os.getenv("STRIPE_API_KEY")

    @app.context_processor
    def inject_variables():
        """
        Inject variables into command line. This is useful for testing the execution environment.
        The environment will be injected as a dictionary with the key " env "
        and the value being the value of the environment variables.


        @return dictionary with the environment variables to inject into the command line.
        """
        return {"env": os.environ}

    if not testing:
        initialize_redis(app)
        initialize_firebase()
