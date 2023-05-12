from redis import Redis
from flask_session import Session
import os


def initialize_redis(app):
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = Redis(
        host="redis-10870.c55.eu-central-1-1.ec2.cloud.redislabs.com",
        port=10870,
        password=os.getenv("REDIS_PASSWORD"),
    )
    Session(app)
