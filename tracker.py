#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring, import-error, redefined-outer-name

import argparse
import cryptohelper
from datetime import datetime
from dbtool import connect_db
from flask import Flask, jsonify, request, make_response, url_for, g
from flask.ext.httpauth import HTTPBasicAuth
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
    user, b64pwd = g.db.execute("""select username, password from users
            where username == ?""", (username,)).fetchone()
    if not user or not cryptohelper.check_pwd(password, b64pwd):
        return False
    return True

#@auth.get_password
#def get_password(username):
#    query = """select password from users
#    where username == ?
#    """
#    password = g.db.execute(query, (username,)).fetchone()
#    if password:
#        return password[0]
#    return


@auth.error_handler
@app.errorhandler(401)
def unauthorized():
    return make_response(
        jsonify({"message": "Unauthorized access"}), 401)


@app.errorhandler(405)
def method_not_allowed():
    return make_response(
        jsonify({"message": "Method not allowed"}), 405)


@app.errorhandler(500)
def internal_server_error():
    return make_response(
        jsonify({"message": "Internal server error"}), 500)


def check_user(user, logged_in):
    if user != logged_in and user is not None:
        return False
    return True


# Aggiunta di un numero di passi per la giornata in corso
@app.route("/v1/days", methods=["POST"])
@app.route("/v2/users/<user>/days", methods=["POST"])
@auth.login_required
def add_day(user=None):
    if not check_user(user, auth.username()):
        return unauthorized()

    if not request.json or not "steps" in request.json:
        return make_response(
            jsonify({"message": "Bad Request: missing step number"}), 400)

    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if day_present(day):
        return make_response(
            jsonify({"message": "Bad Request: item already present"}), 400)

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
def change_day(user=None):
    if not check_user(user, auth.username()):
        return unauthorized()

    if not request.json or not "steps" in request.json:
        make_response(
            jsonify({"message": "Bad Request: missing step number"}), 400)

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
def get_day(date, user=None):
    if not check_user(user, auth.username()):
        return unauthorized()

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
def remove_day(date, user=None):
    if not check_user(user, auth.username()):
        return unauthorized()

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
    return g.db.execute("""select date, nsteps from days
                     where date == ? and username ==?""",
                     (date, auth.username())).fetchone()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dbfile", help="database file name")
    args = parser.parse_args()
    DBFILE = args.dbfile
    app.run()
