from flask import Flask
from views import *
from config import initialize_extensions
import os


def create_app(testing=False):
    if os.getenv("FLASK_ENV") != "production":
        from dotenv import load_dotenv

        load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("PAGE_SECRET_KEY")
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    initialize_extensions(app, testing=testing)

    @app.context_processor
    def inject_variables():
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

if __name__ == "__main__":
    app.run(debug=True)
