from flask import jsonify

from bitorb.errors import APIInvalidUsage
from bitorb import app


@app.errorhandler(APIInvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response