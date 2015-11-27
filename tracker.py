#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring, import-error, redefined-outer-name

import argparse
import cryptohelper
from datetime import datetime
from dbtool import connect_db
from flask import Flask, jsonify, request, make_response, url_for, g
from flask.ext.httpauth import HTTPBasicAuth
from functools import wraps
from jsonschema import ValidationError
import json_schema
import os
import sqlite3
app = Flask(__name__)
auth = HTTPBasicAuth()

DBFILE = ""

@app.before_request
def before_request():
    db = getattr(g, "db", None)
    if db is None:
        g.db = connect_db(DBFILE)
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


@auth.verify_password
def verify_password(username, password):
    if not username:
        return False

    resp = g.db.execute("""select username, password from users
            where username == ?""", (username,)).fetchone()

    if not resp:
        return False

    user, b64pwd = resp

    if not user or not cryptohelper.check_pwd(password, b64pwd):
        return False

    return True


def check_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get("user")
        if user != auth.username() and user is not None:
            return unauthorized()
        return func(*args, **kwargs)
    return wrapper


def validate_schema(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            json_schema.VALIDATOR.validate(request.json)
        except ValidationError:
            return bad_req("Non-validating payload")
        return func(*args, **kwargs)
    return wrapper

@app.errorhandler(400)
def bad_req(msg=""):
    err = "Bad Request"
    if msg:
        err = "{0}: {1}".format(err, msg)
    return make_response(jsonify({"message": err}), 400)

@auth.error_handler
@app.errorhandler(401)
def unauthorized():
    return make_response(jsonify({"message": "Unauthorized access"}), 401)


@app.errorhandler(405)
def method_not_allowed():
    return make_response(jsonify({"message": "Method not allowed"}), 405)


@app.errorhandler(500)
def internal_server_error(exception):
    return make_response(jsonify({"message": "Internal server error"}), 500)


# Aggiunta di un numero di passi per la giornata in corso
@app.route("/v1/days", methods=["POST"])
@app.route("/v2/users/<user>/days", methods=["POST"])
@auth.login_required
@check_user
@validate_schema
def add_day(user=None):
    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if day_present(day):
        return bad_req("item already present")

    add(day)
    response = {
        "message": "Created",
        "day": day,
    }

    if user is not None:
        response["uri"] = url_for(
            "get_day", date=date, user=user, _external=True)
    else:
        response["uri"] = url_for("get_day", date=date, _external=True)
    return make_response(jsonify(response), 201)


# Modifica del numero di passi per la giornata in corso
@app.route("/v1/days", methods=["PUT"])
@app.route("/v2/users/<user>/days", methods=["PUT"])
@auth.login_required
@check_user
@validate_schema
def change_day(user=None):
    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if not day_present(day):
        return make_response(jsonify({"message": "Not Found"}), 404)

    # Siccome remove e add usano la data come chiave il seguente codice
    # funziona perché i corpi del giorno rimosso e aggiunto differiscono
    remove(day)
    add(day)
    response = {
        "message": "OK",
        "day": day,
    }

    if user is not None:
        response["uri"] = url_for(
                "get_day", date=date, user=user, _external=True)
    else:
        response["uri"] = url_for("get_day", date=date, _external=True)
    return make_response(jsonify(response), 200)


# Recupero del numero di passi per una data arbitraria
@app.route("/v1/days/<date>", methods=["GET"])
@app.route("/v2/users/<user>/days/<date>", methods=["GET"])
@auth.login_required
@check_user
def get_day(date, user=None):
    day = get_date(date)
    if not day:
        return make_response(
            jsonify({"message": "Not Found"}), 404)

    return make_response(
        jsonify({
            "message": "OK",
            "day": day
        }), 200
    )


# Rimozione dei passi registrati per una data arbitraria
@app.route("/v1/days/<date>", methods=["DELETE"])
@app.route("/v2/users/<user>/days/<date>", methods=["DELETE"])
@auth.login_required
@check_user
def remove_day(date, user=None):
    day = get_date(date)
    if not day:
        return make_response(jsonify({"message": "Not Found"}), 404)

    remove(day)
    return make_response(jsonify({"message": "OK", "day" : day}), 200)


def day_present(day):
    """
    Controlla se il giorno è presente nel database
    """
    query = """select * from users, days
    where days.username == ? and days.date == ?"""
    return g.db.execute(query, (auth.username(), day["date"])).fetchone()


def add(day):
    """
    Aggiunge un giorno al database
    """
    try:
        g.db.execute(
            "insert into days (date, nsteps, username) values (?, ?, ?);",
            (day["date"], day["steps"], auth.username()))
    except sqlite3.IntegrityError:
        return
    g.db.commit()


def remove(day):
    """
    Rimuove un giorno dal database
    """
    g.db.execute("delete from days where date == ? and username == ?",
            (day["date"], auth.username()))
    g.db.commit()


def get_date(date):
    """
    Ritorna un giorno dal database
    """
    date_tup = g.db.execute("""select date, nsteps from days
                     where date == ? and username ==?""",
                     (date, auth.username())).fetchone()
    if date_tup is None:
        return None
    return {"date": date_tup[0], "steps": date_tup[1]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbfile", help="database file name")
    args = parser.parse_args()

    DBFILE = args.dbfile or os.getenv("TRACKER_DB")
    if not DBFILE:
        exit("Please specify a database")

    app.run()
