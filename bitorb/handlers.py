from flask import jsonify, redirect, request, render_template, make_response
from urllib.parse import quote

from bitorb.errors import APIInvalidUsage, RequiresLogin, UserNotFound
from bitorb import app


@app.errorhandler(APIInvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(RequiresLogin)
def redirect_to_login(e):
    return redirect("/login?r=%s" % quote(request.url), 302)


@app.errorhandler(UserNotFound)
def user_not_found(e):
    return make_response(render_template("user_not_found.html"), 400)
