from sqlalchemy import sql

from flask import render_template, request, redirect

from bitorb.database import Establishment, engine

from bitorb import app


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    if request.cookies.get("auth_token"):
        return redirect("/user")
    else:
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


@app.route("/create_tokens")
def create_tokens():
    return render_template("create_tokens.html")


@app.route("/user")
def user():
    try:
        return render_template("user.html", user_id=request.args["id"])
    except KeyError:
        return render_template("user.html", user_id=None)


@app.route("/user/<estab_id>/<username>")
def other_user(estab_id, username):
    pass


@app.route("/logout")
def logout():
    return render_template("logout.html")

# @app.route("/usrgen/<user_id>/<item>")
# def get_user_upload(user_id, item):
#     pass
