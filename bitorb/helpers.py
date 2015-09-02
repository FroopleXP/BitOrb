import random
from hashlib import sha256

from itsdangerous import Signer
from sqlalchemy import sql

from bitorb.main import app
from bitorb.database import User, Establishment, engine
from bitorb.errors import AuthTokenInvalid, UserNotFound, EstabNotFound


from pprint import pprint
import inspect

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


def gen_login_token(user):
    token = "-".join((user.username, str(user.establishment), gen_password(8, "0123456789")))
    token = token.encode("utf8")
    return signer.sign(token).decode("utf8")


def get_user_from_token(token):
    if not signer.validate(token):
        raise AuthTokenInvalid()

    split = signer.unsign(token).decode("utf8").split("-")

    username = split[0]
    estab_id = split[1]

    conn = engine.connect()
    query = sql.select([User]).where(
        (User.establishment == estab_id) &
        (User.username == username)
    )
    res = conn.execute(query)

    if res.rowcount == 1:
        return res.fetchone()
    else:
        raise AuthTokenInvalid()


def get_user_from_id(user_id):
    conn = engine.connect()
    query = sql.select([User]).where(
        (User.id == user_id)
    )
    res = conn.execute(query)

    if res.rowcount == 1:
        return res.fetchone()
    else:
        raise UserNotFound()


def get_estab_from_id(estab_id):
    conn = engine.connect()
    query = sql.select([Establishment]).where(
        (Establishment.id == estab_id)
    )
    res = conn.execute(query)

    if res.rowcount == 1:
        return res.fetchone()
    else:
        raise EstabNotFound()


def debug(obj):
    pprint(inspect.getmembers(obj))
