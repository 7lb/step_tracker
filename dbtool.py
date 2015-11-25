#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring

import argparse
from cryptohelper import hash_pwd
import sqlite3

DEV_USERS = (
    ("admin", hash_pwd("admin")),
    ("foo", hash_pwd("bar")),
    ("pippo", hash_pwd("pluto"))
)

def connect_db(dbfile):
    return sqlite3.connect(dbfile)


def init_db(schema, dbfile):
    conn = connect_db(dbfile)
    with open(schema, "r") as fd:
        conn.cursor().executescript(fd.read())
    conn.commit()
    conn.close()


def populate_db(dbfile, userpasses=DEV_USERS):
    conn = connect_db(dbfile)
    query = "insert into users (username, password) values (?, ?);"
    for elem in userpasses:
        conn.execute(query, elem)
    conn.commit()
    conn.close()


def clear_db(dbfile):
    conn = connect_db(dbfile)
    conn.cursor().execute("delete from days")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--dbfile", help="database file name")
    parser.add_argument("-s", "--schema",
            help="the database schema file")
    parser.add_argument("--init", help="reset the db",
            action="store_true")
    parser.add_argument("--dev", help="init and populate dev db",
            action="store_true")
    parser.add_argument("--test", help="init test db",
            action="store_true")
    args = parser.parse_args()

    if not args.schema:
        exit("Please provide a database schema")

    if args.init:
        init_db(args.schema, args.dbfile)
    if args.dev:
        init_db(args.schema, args.dbfile)
        populate_db(args.dbfile)
    if args.test:
        init_db(args.schema, args.dbfile)
