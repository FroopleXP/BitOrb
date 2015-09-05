from sqlalchemy import sql

from flask import render_template, request, redirect, make_response

from bitorb.database import Establishment, User, engine

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


@app.route("/user/<estab_code_name>/<username>")
def other_user(estab_code_name, username):
    estab_code_name = estab_code_name.upper()
    username = username.lower()

    conn = engine.connect()
    query = sql.select((Establishment,)).where(
        Establishment.code_name == estab_code_name
    ).limit(1)
    res = conn.execute(query)
    if res.rowcount == 0:
        return make_response("Invalid estab_code_name", 404)

    estab_id = res.fetchone()["id"]

    query = sql.select((User, )).where(
        (User.establishment == estab_id) &
        (User.username == username)
    ).limit(1)
    res = conn.execute(query)
    if res.rowcount == 0:
        return make_response("User not found", 404)
    else:
        return render_template("user.html", user_id=res.fetchone()["id"])


@app.route("/logout")
def logout():
    return render_template("logout.html")

# @app.route("/usrgen/<user_id>/<item>")
# def get_user_upload(user_id, item):
#     pass
