from bitorb import app
from bitorb.helpers import get_user_from_token, get_user_from_id, get_estab_from_id
from bitorb.errors import RequiresLogin, AuthTokenInvalid, RequiresHTTPS
from bitorb.config import config
from flask import request


def get_user(user_id=None, required=True):
    if user_id is None:
        auth_token = request.cookies.get("auth_token")
        if auth_token is None:
            if required:
                raise RequiresLogin()
            else:
                return None

        try:
            caller = get_user_from_token(auth_token)
        except AuthTokenInvalid:
            if required:
                raise RequiresLogin()
            else:
                return None
        return caller
    else:
        return get_user_from_id(user_id)


def get_estab(estab_id=None, required=True):
    if estab_id is None:
        estab_id = get_user().establishment

    return get_estab_from_id(estab_id)


def get_site_name():
    return config["site"]["name"]


def get_secure(required=True):

    if request.url.startswith("http://"):
        if (config["secure"]["allow-redirect"] or config["secure"]["enabled"]) and required:
            raise RequiresHTTPS()
        else:
            return False
    else:
        return True


@app.context_processor
def utility_processor():
    return {
        "get_user": get_user,
        "get_estab": get_estab,
        "get_site_name": get_site_name,
        "get_secure": get_secure
    }

