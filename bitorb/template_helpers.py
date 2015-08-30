from bitorb import app
from bitorb.helpers import get_user_from_token
from bitorb.errors import RequiresLogin
from flask import request


def get_user():
    auth_token = request.cookies.get("auth_token")
    if auth_token is None:
        raise RequiresLogin()

    caller = get_user_from_token(auth_token)
    if not caller:
        raise RequiresLogin()
    return caller


@app.context_processor
def utility_processor():
    return {
        "get_user": get_user
    }

