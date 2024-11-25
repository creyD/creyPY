import requests
from cachetools import TTLCache, cached

from .common import AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN

cache = TTLCache(maxsize=100, ttl=600)


@cached(cache)
def get_management_token() -> str:
    response = requests.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience": f"https://{AUTH0_DOMAIN}/api/v2/",  # This should be the management audience
            "grant_type": "client_credentials",
        },
        timeout=5,  # Add a timeout parameter to avoid hanging requests
    ).json()
    return response["access_token"]
