from sqlalchemy import sql

from flask import Flask, render_template
from itsdangerous import Signer

from bitorb.database import Establishment, engine
from bitorb.config import config

from bitorb import app

signer = Signer(app.secret_key)


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
    )
    conn = engine.connect()
    res = conn.execute(query)

    return render_template("login.html", establishments=res.fetchall())


@app.route("/new_estab")
def estab_create():
    return render_template("new_estab.html")



if __name__ == '__main__':
    app.run(config["server"]["address"], config["server"]["port"])

