from bitorb import app
from bitorb.helpers import get_user_from_token, get_user_from_id, get_estab_from_id
from bitorb.errors import RequiresLogin, AuthTokenInvalid
from flask import request


def get_user(user_id=None):
    if user_id is None:
        auth_token = request.cookies.get("auth_token")
        if auth_token is None:
            raise RequiresLogin()

        try:
            caller = get_user_from_token(auth_token)
        except AuthTokenInvalid:
            raise RequiresLogin
        return caller
    else:
        return get_user_from_id(user_id)


def get_estab(estab_id=None):
    if estab_id is None:
        estab_id = get_user().establishment

    return get_estab_from_id(estab_id)


@app.context_processor
def utility_processor():
    return {
        "get_user": get_user,
        "get_estab": get_estab
    }

