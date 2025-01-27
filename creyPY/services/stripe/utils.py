import os

import stripe
from dotenv import load_dotenv

load_dotenv()


def get_stripe_api():
    stripe.api_key = os.getenv("STRIPE_API_KEY", "")
    return stripe
