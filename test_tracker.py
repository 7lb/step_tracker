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
        cls.url_v1 = "http://127.0.0.1:5000/v1/days"
        cls.url_v2 = "http://127.0.0.1:5000/v2/users/{0}/days"
        populate_db(DBFILE, map(
            lambda t: (t[0], hash_pwd(t[1])),
            cls.users))

    def setUp(self):
        clear_db(DBFILE)

    def test_bad_auth_v1(self):
        resp = requests.post(
            self.url_v1, json={"steps":999}, auth=("nouser", "nopwd"))
        self.assertEqual(resp.status_code, 401)

    def test_bad_auth_v2(self):
        # Qui si testa se un user cerca di modificare i dati relativi a un
        # altro utente
        for auth_user, pwd in self.users:
            for target_user, _ in self.users:
                if auth_user != target_user:
                    url = self.url_v2.format(target_user)
                    resp = requests.post(
                        url, json={"steps":100}, auth=(auth_user, pwd))
                    self.assertEqual(resp.status_code, 401)

        # Qui si testa se un user cerca di modificare i dati relativi a sè
        # sesso, ma lo user non esiste
        wrong_user = ("nouser", "nopwd")
        url_wrong_user = self.url_v2.format(wrong_user[0])
        resp = requests.post(
            url_wrong_user, json={"steps":100}, auth=wrong_user)
        self.assertEqual(resp.status_code, 401)

    def test_not_found_v1(self):
        for user, pwd in self.users:
            url = self.url_v1 + "/1900-01-01"
            resp = requests.get(url, auth=(user, pwd))
            self.assertEqual(resp.status_code, 404)

    def test_not_found_v2(self):
        for user, pwd in self.users:
            url = self.url_v2.format(user) + "/1900-01-01"
            resp = requests.get(url, auth=(user, pwd))
            self.assertEqual(resp.status_code, 404)

    def test_post_v1(self):
        for user, pwd in self.users:
            resp = requests.post(
                self.url_v1, json={"steps":100}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)

            resp = requests.post(
                self.url_v1, json={"steps":100}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 400)

    def test_post_v2(self):
        for user, pwd in self.users:
            url = self.url_v2.format(user)

            resp = requests.post(url, json={"steps":100}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)

            resp = requests.post(url, json={"steps":100}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 400)

    def test_get_v1(self):
        for user, pwd in self.users:
            resp = requests.post(
                self.url_v1, json={"steps":1001}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)

            get_uri = resp.json()["uri"]
            resp = requests.get(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)

    def test_get_v2(self):
        for user, pwd in self.users:
            url = self.url_v2.format(user)
            resp = requests.post(
                url, json={"steps":77}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)

            get_uri = resp.json()["uri"]
            resp = requests.get(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)

    def test_put_v1(self):
        for user, pwd in self.users:
            resp = requests.post(
                self.url_v1, json={"steps":11}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.json()["day"]["steps"], 11)

            resp = requests.put(
                self.url_v1, json={"steps":22}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()["day"]["steps"], 22)

    def test_put_v2(self):
        for user, pwd in self.users:
            url = self.url_v2.format(user)
            resp = requests.post(
                url, json={"steps":11}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.json()["day"]["steps"], 11)

            resp = requests.put(
                url, json={"steps":22}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()["day"]["steps"], 22)

    def test_delete_v1(self):
        for user, pwd in self.users:
            resp = requests.post(
                self.url_v1, json={"steps":280}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.json()["day"]["steps"], 280)

            get_uri = resp.json()["uri"]
            resp = requests.delete(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)

            resp = requests.delete(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 404)

    def test_delete_v2(self):
        for user, pwd in self.users:
            url = self.url_v2.format(user)
            resp = requests.post(
                url, json={"steps":280}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.json()["day"]["steps"], 280)

            get_uri = resp.json()["uri"]
            resp = requests.delete(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)

            resp = requests.delete(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 404)

if __name__ == "__main__":
    unittest.main()
