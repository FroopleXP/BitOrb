from bitorb import app
from bitorb.helpers import get_user_from_token
from flask import redirect, request

from urllib.parse import quote



class RequiresLogin(Exception):
    status_code = 401
    status = "failed"
    message = "This method requires login."

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["status"] = self.status
        rv['message'] = self.message
        return rv


@app.errorhandler(RequiresLogin)
def redirect_to_login(e):
    return redirect("/login?r=%s" % quote(request.url), 302)


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

