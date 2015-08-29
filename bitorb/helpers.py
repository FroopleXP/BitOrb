from functools import wraps
import random
from hashlib import sha256

from flask import jsonify, make_response

from bitorb.main import app


class InvalidAPIUsage(Exception):
    status_code = 400
    status = "failed"

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["status"] = self.status
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def gen_password(length=8, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    password = ""
    for char in range(length):
        password += chars[random.randint(0, len(chars) - 1)]
    return password


def crypt_hash(string_to_hash):
    hasher = sha256()
    hasher.update(string_to_hash.encode("utf8"))
    return hasher.digest()


def add_response_headers(headers=None):
    """This decorator adds the headers passed in to the response"""
    headers = headers or {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def allow_localhost(f):
    """This decorator passes Access-Control-Allow-Origin: *"""
    @wraps(f)
    @add_response_headers({'Access-Control-Allow-Origin': '*'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function
