from sqlalchemy import sql

from flask import request, make_response, jsonify
import sqlalchemy

from bitorb.helpers import allow_localhost, InvalidAPIUsage, crypt_hash, gen_password
from bitorb.main import app
from bitorb.database import Establishment, User, engine


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
def api_user_create():
    return "Not implemented"
