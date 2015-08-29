from sqlalchemy import sql

from flask import request, make_response, jsonify
import itsdangerous
import sqlalchemy

from bitorb.helpers import allow_localhost, InvalidAPIUsage, crypt_hash, gen_password, gen_login_token, signer, get_user_from_token
from bitorb.main import app
from bitorb.database import Establishment, User, engine


@app.route("/api/v1/estab/create", methods=["POST"])
@allow_localhost
def api_estab_create():
    try:
        name = request.form["name"]
    except KeyError as e:
        # do something more useful here
        raise InvalidAPIUsage("Name must be specified.", 400)

    try:
        user = request.form["user"] or ""
        password = request.form["password"] or ""

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
@allow_localhost
def api_user_create():
    return "Not implemented"


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
        raise InvalidAPIUsage("something was missing", 400)

    estab_id = int(estab_id)
    username = username.lower()
    pass_hash = crypt_hash(password)

    conn = engine.connect()
    query = sql.select([User]).where(
        (User.establishment == estab_id) &
        (User.username == username) &
        (User.pass_hash == pass_hash)
    )
    res = conn.execute(query)

    if res.rowcount == 1:
        # successful login, make a token
        return make_response(jsonify({
            "status": "success",
            "message": "You have successfully logged in.",
            "auth_token": gen_login_token(res.fetchall()[0])
        }), 200)

    else:
        return make_response(jsonify({
            "status": "failed",
            "message": "Username, password and establishment combination was incorrect."
        }), 200)


@app.route("/api/v1/user/test_login", methods=["POST"])
@allow_localhost
def api_user_login_test():
    try:
        token = request.form["auth_token"]
    except KeyError as e:
        raise InvalidAPIUsage("auth_token field missing", 400)

    user = get_user_from_token(token)
    res = user is not None
    print(user)

    if res:
        return make_response(jsonify({
            "status": "success",
            "message": "auth_token is valid. Logged in as %s." % " ".join((user.first_name, user.last_name))
        }), 200)
    else:
        return make_response(jsonify({
            "status": "failed",
            "message": "auth_token is invalid"
        }), 200)
