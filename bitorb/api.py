from sqlalchemy import sql

from flask import request, make_response, jsonify
import sqlalchemy
import re

from bitorb.helpers import crypt_hash, gen_password, gen_login_token, get_user_from_token
from bitorb.errors import APIInvalidUsage, APIMissingField, APIInvalidField, AuthTokenInvalid
from bitorb.main import app
from bitorb.database import Establishment, User, Token, engine

from pprint import pprint


@app.route("/api/v1/estab/create", methods=["POST"])
def api_estab_create():
    try:
        name = request.form["name"]
    except KeyError as e:
        # do something more useful here
        raise APIMissingField(e.args[0])

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
        raise APIMissingField("name")

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


@app.route("/api/v1/token/add", methods=["POST"])
def api_token_add():
    try:
        auth_token = request.form["auth_token"]

        token_value = request.form["token_value"]
    except KeyError as e:
        raise APIMissingField(e.args[0])

    token_number = 1

    try:
        token_code = request.form["token_code"]
    except KeyError as e:
        token_code = None
        try:
            token_number = request.form["token_number"]
        except KeyError as e:
            token_number = 1

    caller = get_user_from_token(auth_token)

    token_number = min(100, int(token_number))
    if token_number == 0:
        raise APIInvalidField("token_number")

    if caller.rank != "admin":
        if caller.credits < token_value * token_number:
            raise APIInvalidUsage("M")  # TODO: add better error

    tokens = []

    if token_number == 1 and token_value:
        if re.match("[^A-Z0-9]", token_value) or len(token_value) != 10:
            return make_response(jsonify({
                "status": "failed",
                "message": "Invalid code."
            }))

        tokens.append({
            "code": token_code,
            "value": token_value,
            "creator": caller.id,
            "redeemed": False
        })

    else:
        for token in range(token_number):
            tokens.append({
                "code": gen_password(10),
                "value": token_value,
                "creator": caller.id,
                "redeemed": False
            })

    pprint(tokens)

    conn = engine.connect()
    query = sql.insert(Token, tokens)
    res = conn.execute(query)

    if res.inserted_primary_key:
        return make_response(jsonify({
            "status": "success",
            "message": "%s codes have been generated with a value of %s credits." % (
                str(token_number),
                str(token_value)
            ),
            "tokens": list({"code": x["code"], "value": x["value"]} for x in tokens)
        }))


@app.route("/api/v1/token/redeem", methods=["POST"])
def api_token_redeem():
    try:
        auth_token = request.form["auth_token"]

        token_code = request.form["token_code"]
    except KeyError as e:
        raise APIMissingField(e.args[0])

    caller = get_user_from_token(auth_token)

    conn = engine.connect()

    query = sql.select([Token]).where(Token.code == token_code).limit(1)
    res = conn.execute(query)
    try:
        token = res.fetchall()[0]
    except IndexError:
        raise APIInvalidField("token_code", 200)

    query1 = sql.update(Token).where(Token.id == token.id).values({
        Token.redeemed: True,
        Token.redeemer: caller.id
    })
    query2 = sql.update(User).where(User.id == caller.id).values({
        User.credits: caller.credits + token.value
    })
    res1 = conn.execute(query1)
    res2 = conn.execute(query2)

    if res1.inserted_primary_key and res2.inserted_primary_key:
        return make_response(jsonify({
            "status": "success",
            "message": "Token successfully redeemed",
            "new_balance": caller.credits + token.value
        }))


@app.route("/api/v1/user/create", methods=["POST"])
def api_user_create():
    try:
        auth_token = request.form["auth_token"]

        user_first_name = request.form["user_first_name"]
        user_last_name = request.form["user_last_name"]
        user_other_names = request.form["user_other_names"] or None

        user_email = request.form["user_email"] or None
        user_username = request.form["user_first_name"]
        user_password = request.form["user_password"] or gen_password(8)

        user_rank = request.form["rank"]

        if "" in (user_first_name, user_last_name, user_username, user_password, user_rank):
            raise KeyError

    except KeyError:
        raise APIMissingField(e.args[0])

    caller = get_user_from_token(auth_token)

    if caller.rank != "admin":
        return make_response(jsonify({
            "status": "failed",
            "message": "You do not have a high enough rank to create users."
        }))

    conn = engine.connect()
    query = sql.insert(User, {
        User.first_name: user_first_name,
        User.last_name: user_last_name,
        User.other_names: user_last_name,

        User.email: user_email,
        User.username: user_username,
        User.pass_hash: crypt_hash(user_password),

        User.rank: user_rank
    })
    res = conn.execute(query)

    if res.inserted_primary_key:
        return make_response(jsonify({
            "status": "success",
            "message": "User created",
            "user_id": res.inserted_primary_key
        }))
    else:
        return make_response(jsonify({
            "status": "failed",
            "message": "Unknown error"
        }))


@app.route("/api/v1/user/login", methods=["POST"])
def api_user_login():
    print(request.form.to_dict())
    try:
        estab_id = request.form["estab_id"]
        username = request.form["username"]
        password = request.form["password"]

        if estab_id == "":
            raise APIMissingField("estab_id")
        elif username == "":
            raise APIMissingField("username")
        elif password == "":
            raise APIMissingField("password")

    except KeyError as e:
        raise APIMissingField(e.args[0])
    try:
        estab_id = int(estab_id)
    except ValueError:
        raise APIInvalidField("estab_id")

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
def api_user_login_test():
    try:
        token = request.form["auth_token"]
    except KeyError as e:
        raise APIMissingField(e.args[0])

    try:
        user = get_user_from_token(token)
        return make_response(jsonify({
            "status": "success",
            "message": "auth_token is valid. Logged in as %s." % " ".join((user.first_name, user.last_name))
        }), 200)

    except AuthTokenInvalid:
        return make_response(jsonify({
            "status": "failed",
            "message": "auth_token is invalid"
        }), 200)
