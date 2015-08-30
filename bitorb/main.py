from sqlalchemy import sql

from flask import render_template
from itsdangerous import Signer

from bitorb.database import Establishment, engine

from bitorb import app



@app.route('/')
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    query = sql.select(
        (
            Establishment.id,
            Establishment.full_name
        )
    ).order_by(Establishment.full_name)
    conn = engine.connect()
    res = conn.execute(query)

    return render_template("login.html", establishments=res.fetchall())


@app.route("/new_estab")
def estab_create():
    return render_template("new_estab.html")


@app.route("/test_token")
def test_token():
    return render_template("test_login.html")


@app.route("/new_user")
def new_user():
    return render_template("new_user.html")
