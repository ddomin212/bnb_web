""" This module is used to initialize redis user session. """
import os
from redis import Redis
from flask_session import Session


def initialize_redis(app):
    """
    Initialize redis session. This is called by : func : ` ~flask. Flask. init_redis `

    @param app - Flask application to be
    """
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = Redis(
        host="redis-10870.c55.eu-central-1-1.ec2.cloud.redislabs.com",
        port=10870,
        password=os.getenv("REDIS_PASSWORD"),
    )
    Session(app)
