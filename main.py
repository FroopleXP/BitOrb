from flask import Flask, request, make_response, jsonify, render_template
from itsdangerous import Signer

from database import Establishment, User, engine
import sqlalchemy
from sqlalchemy import sql

from functools import wraps

import inspect
from pprint import pprint

import random

from hashlib import sha256

app = Flask(__name__)
app.debug = True
app.secret_key = "uP7DVYBKXo7OV.h!"

signer = Signer(app.secret_key)

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
    """This decorator passes X-Robots-Tag: noindex"""
    @wraps(f)
    @add_response_headers({'Access-Control-Allow-Origin': '*'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


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


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route("/login")
def login():
    query = sql.select(
        (
            Establishment.id,
            Establishment.full_name
        )
    )
    conn = engine.connect()
    res = conn.execute(query)

    return render_template("login.html", establishments=res.fetchall())


@app.route("/new_estab")
def estab_create():
    return render_template("new_estab.html")


@app.route("/api/v1/user/login", methods=["POST"])
@allow_localhost
def api_user_login():
    try:
        estab_id = request.form["estab_id"]
        username = request.form["username"]
        password = request.form["password"]

        if "" in (estab_id, username, password):
            raise KeyError

    except KeyError as e:
        print(e.args)
        raise InvalidAPIUsage("somethign was missing", 400)

    estab_id = int(estab_id)
    username = username.lower()
    pass_hash = crypt_hash(password)


@app.route("/api/v1/estab/create", methods=["POST"])
@allow_localhost
def api_estab_create():
    pprint(request.form.to_dict())
    try:
        name = request.form["name"]
    except KeyError as e:
        # do something more useful here
        raise InvalidAPIUsage("Name must be specified.", 400)

    try:
        user = request.form["user"] or None
        password = request.form["password"] or None

        if "" in (user, password):
            raise KeyError

        default_user = False
    except KeyError as e:
        user = "Admin"
        password = gen_password(8)
        default_user = True

    if name == "":
        raise InvalidAPIUsage("Name cannot be empty", 400)

    conn = engine.connect()
    query = sql.Insert(Establishment, {
        Establishment.full_name: name
    })
    try:
        res = conn.execute(query)
    except sqlalchemy.exc.IntegrityError as e:
        print(e)
        return make_response(jsonify({
            "status": "failed",
            "message": "Name is in use."
        }), 400)
    estab_id = res.inserted_primary_key[0]

    query = sql.insert(User, {
        User.first_name: "Admin",
        User.last_name: "User",
        User.rank: "admin",

        User.username: user,
        User.pass_hash: crypt_hash(password),
        User.establishment: estab_id
    })
    res = conn.execute(query)

    if default_user:
        return make_response(jsonify({
            "status": "success",
            "message": "Establishment was created! (User does not work yet...)",
            "id": estab_id,
            "username": user,
            "password": password
        }))
    else:
        return make_response(jsonify({
            "status": "success",
            "message": "Establishment was created! (User does not work yet...)",
            "id": estab_id,
            "username": user,
            "password": "********"
        }))


@app.route("/api/v1/user/create", methods=["POST"])
def api_user_create():
    return "Not implemented"

# @app.route("/api/v1/estab/create", methods=["POST"])
# def api_estab_create():
#     try:
#         first_name = request.form["first_name"]
#         last_name = request.form["last_name"]
#         other_names = request.form["other_names"]
#
#         email = request.form["email"]
#         username = request.form["username"]
#         password = request.form["password"]
#
#         estab_id = request.form["estab_id"]
#         rank = request.form["rank"]
#     except KeyError as e:
#         print(e)
#
#     return "Hi"

if __name__ == '__main__':
    app.run("0.0.0.0")

