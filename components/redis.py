""" This module is used to initialize redis user session. """
import os

from flask_session import Session
from redis import Redis

class RedisComponent:
    def __init__(self, app):
        """
        Initialize redis session. This is called by : func : ` ~flask. Flask. init_redis `

        @param app - Flask application to be
        """
        app.config["SESSION_TYPE"] = "redis"
        app.config["SESSION_REDIS"] = Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            password=os.getenv("REDIS_PASSWORD"),
        )
        Session(app)
