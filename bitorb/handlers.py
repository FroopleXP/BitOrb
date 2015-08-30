from flask import jsonify, redirect, request
from urllib.parse import quote

from bitorb.errors import APIInvalidUsage, RequiresLogin
from bitorb import app


@app.errorhandler(APIInvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(RequiresLogin)
def redirect_to_login(e):
    return redirect("/login?r=%s" % quote(request.url), 302)
