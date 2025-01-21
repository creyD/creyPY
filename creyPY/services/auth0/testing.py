USER_OBJ = {
    "auth0|testing": {
        "created_at": "2023-08-15T13:25:31.507Z",
        "email": "test@test.org",
        "email_verified": True,
        "identities": [
            {
                "connection": "Username-Password-Authentication",
                "provider": "auth0",
                "user_id": "testing",
                "isSocial": False,
            }
        ],
        "name": "Test Tester",
        "nickname": "testing",
        "picture": "https://avatars.githubusercontent.com/u/15138480?v=4",
        "updated_at": "2024-01-17T12:36:37.300Z",
        "user_id": "auth0|testing",
        "user_metadata": {},
        "last_password_reset": "2024-01-17T11:42:08.761Z",
        "last_ip": "127.0.0.1",
        "last_login": "2024-01-17T11:43:09.620Z",
        "logins_count": 1,
    },
    "auth0|new_user": {
        "created_at": "2023-08-15T13:25:31.507Z",
        "email": "test2@test.org",
        "email_verified": True,
        "identities": [
            {
                "connection": "Username-Password-Authentication",
                "provider": "auth0",
                "user_id": "testing",
                "isSocial": False,
            }
        ],
        "name": "Test Tester 2",
        "nickname": "testing 2",
        "picture": "https://avatars.githubusercontent.com/u/15138481?v=4",
        "updated_at": "2024-01-17T12:36:37.303Z",
        "user_id": "auth0|new_user",
        "user_metadata": {},
        "last_password_reset": "2024-01-17T11:42:08.759Z",
        "last_ip": "127.0.0.1",
        "last_login": "2024-01-17T11:43:09.618Z",
        "logins_count": 1,
    },
}


def get_user_auth0(sub, *args, **kwargs) -> dict:
    return USER_OBJ[sub]


def patch_user_auth0(input_obj: dict, sub, *args, **kwargs) -> dict:
    USER_OBJ[sub].update(input_obj)
    return get_user_auth0(sub)


def get_user_auth0_metadata(sub, *args, **kwargs) -> dict:
    return USER_OBJ[sub]["user_metadata"]


def check_company_auth0(*args, **kwargs) -> bool:
    return True


def auth0_sub_to_profile(sub: str) -> dict:
    return {
        "email": USER_OBJ[sub]["email"],
        "name": USER_OBJ[sub]["name"],
        "picture": USER_OBJ[sub]["picture"],
        "company_ids": USER_OBJ[sub]["user_metadata"]["company_ids"],
    }


def auth0_sub_to_public(sub: str) -> dict:
    return {
        "email": USER_OBJ[sub]["email"],
        "name": USER_OBJ[sub]["name"],
        "picture": USER_OBJ[sub]["picture"],
    }


def patch_user_auth0_metadata(input_obj: dict, sub, *args, **kwargs) -> dict:
    USER_OBJ[sub]["user_metadata"].update(input_obj)
    return get_user_auth0_metadata(sub)


def set_company_id(sub: str, company_id: str):
    if sub not in USER_OBJ:
        USER_OBJ[sub] = {}
    USER_OBJ[sub]["user_metadata"] = {"company_ids": [company_id]}
