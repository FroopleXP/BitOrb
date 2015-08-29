from bitorb import app
from flask import redirect, request


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
    return redirect("/login", 302)


def require_login():
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        raise RequiresLogin()
    return ""


@app.context_processor
def utility_processor():
    return {
        "require_login": require_login
    }

