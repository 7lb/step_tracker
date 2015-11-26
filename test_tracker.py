#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring, too-many-public-methods

from dbtool import init_db, populate_db, clear_db
from cryptohelper import hash_pwd
import requests
import unittest

DBFILE = "dbstuff/test.db"
SCHEMA = "dbstuff/schema.sql"

class TrackerTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db(SCHEMA, DBFILE)
        cls.users = (
            ("user", "pass"),
            ("name", "word"),
            ("leeloo", "multipass"),
        )
        populate_db(DBFILE, map(
            lambda t: (t[0], hash_pwd(t[1], rounds=1)),
            cls.users))

    def setUp(self):
        clear_db(DBFILE)

    def test_post_v1(self):
        for name, pwd in self.users:
            url = "http://{0}:{1}@127.0.0.1:5000/v1/days".format(name, pwd)

            resp = requests.post(url, json={"steps":"100"})
            self.assertEqual(resp.status_code, 201)

            resp = requests.post(url, json={"steps":"100"})
            self.assertEqual(resp.status_code, 400)

    def test_post_v2(self):
        for name, pwd in self.users:
            url = "http://{0}:{1}@127.0.0.1:5000/v2/users/{0}/days".format(
                name, pwd)

            resp = requests.post(url, json={"steps":"100"})
            self.assertEqual(resp.status_code, 201)

            resp = requests.post(url, json={"steps":"100"})
            self.assertEqual(resp.status_code, 400)

    def test_bad_auth_v1(self):
        url = "http://username:password@127.0.0.1:5000/v1/days"
        resp = requests.post(url, json={"steps":"999"})
        self.assertEqual(resp.status_code, 401)

    def test_bad_auth_v2(self):
        url = "http://{0}:{1}@127.0.0.1:5000/v2/users/{2}/days"
        for auth_user, pwd in self.users:
            for target_user, _ in self.users:
                if auth_user != target_user:
                    resp = requests.post(
                        url.format(auth_user, pwd, target_user),
                        json={"steps":"100"})
                    self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
