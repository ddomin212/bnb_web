from .firebase import initialize_firebase, fetch_db
from .redis import initialize_redis
import stripe
import os


def initialize_extensions(app, testing=False):
    if not testing:
        initialize_redis(app)
        initialize_firebase()
    stripe.api_key = os.getenv("STRIPE_API_KEY")
