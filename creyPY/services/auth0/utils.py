from typing import Optional

import jwt
import requests
from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from creyPY.helpers import create_random_password

from .common import (
    AUTH0_ALGORIGHM,
    AUTH0_AUDIENCE,
    AUTH0_CLIENT_ID,
    AUTH0_DOMAIN,
    AUTH0_ISSUER,
)
from .exceptions import UnauthenticatedException, UnauthorizedException
from .manage import get_management_token

JWKS_CLIENT = jwt.PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")


async def verify(
    request: Request,
    token: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False)),
) -> str:
    if token is None:
        raise UnauthenticatedException

    # This gets the 'kid' from the passed token
    try:
        signing_key = JWKS_CLIENT.get_signing_key_from_jwt(token.credentials).key
    except jwt.exceptions.PyJWKClientError as error:
        raise UnauthorizedException(str(error))
    except jwt.exceptions.DecodeError as error:
        raise UnauthorizedException(str(error))

    try:
        payload = jwt.decode(
            token.credentials,
            signing_key,
            algorithms=[AUTH0_ALGORIGHM],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )
    except Exception as error:
        raise UnauthorizedException(str(error))

    return payload["sub"]


### GENERIC AUTH0 CALLS ###
def get_user(sub) -> dict:
    re = requests.get(
        f"https://{AUTH0_DOMAIN}/api/v2/users/{sub}",
        headers={"Authorization": f"Bearer {get_management_token()}"},
        timeout=5,
    )
    if re.status_code != 200:
        raise HTTPException(re.status_code, re.json())
    return re.json()


def patch_user(input_obj: dict, sub) -> dict:
    re = requests.patch(
        f"https://{AUTH0_DOMAIN}/api/v2/users/{sub}",
        headers={"Authorization": f"Bearer {get_management_token()}"},
        json=input_obj,
        timeout=5,
    )
    if re.status_code != 200:
        raise HTTPException(re.status_code, re.json())
    return re.json()


### USER METADATA CALLS ###
def get_user_metadata(sub) -> dict:
    try:
        return get_user(sub).get("user_metadata", {})
    except:
        return {}


def patch_user_metadata(input_obj: dict, sub) -> dict:
    return patch_user({"user_metadata": input_obj}, sub)


def clear_user_metadata(sub) -> dict:
    return patch_user({"user_metadata": {}}, sub)


def request_verification_mail(sub: str) -> None:
    re = requests.post(
        f"https://{AUTH0_DOMAIN}/api/v2/jobs/verification-email",
        headers={"Authorization": f"Bearer {get_management_token()}"},
        json={"user_id": sub},
        timeout=5,
    )
    if re.status_code != 201:
        raise HTTPException(re.status_code, re.json())
    return re.json()


def create_user_invite(email: str, company_id: str) -> dict:
    re = requests.post(
        f"https://{AUTH0_DOMAIN}/api/v2/users",
        headers={"Authorization": f"Bearer {get_management_token()}"},
        json={
            "email": email,
            "connection": "Username-Password-Authentication",
            "password": create_random_password(),
            "verify_email": False,
            "app_metadata": {"invitedToMyApp": True},
            "user_metadata": {"company_ids": [company_id]},
        },
        timeout=5,
    )
    if re.status_code != 201:
        raise HTTPException(re.status_code, re.json())
    return re.json()


def delete_user_invite(user_id: str) -> None:
    re = requests.delete(
        f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}",
        headers={"Authorization": f"Bearer {get_management_token()}"},
        timeout=5,
    )
    if re.status_code != 204:
        raise HTTPException(re.status_code, re.json())


def password_change_mail(email: str) -> bool:
    re = requests.post(
        f"https://{AUTH0_DOMAIN}/dbconnections/change_password",
        headers={"Authorization": f"Bearer {get_management_token()}"},
        json={
            "client_id": AUTH0_CLIENT_ID,
            "email": email,
            "connection": "Username-Password-Authentication",
        },
        timeout=5,
    )

    if re.status_code != 200:
        raise HTTPException(re.status_code, re.json())
    return True
