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
        # Nota bene: Questo metodo viene richiamato all'inizio della suite di
        # test, non prima di ogni test (quella è la funzione setUp), quindi
        # tutte le operazioni e le assegnazioni qui dentro verranno eseguite
        # sempre e solo una volta, prima di tutti i test singoli
        init_db(SCHEMA, DBFILE)
        cls.users = (
            ("user", "pass"),
            ("name", "word"),
            ("leeloo", "multipass"),
        )
        cls.url = "http://127.0.0.1:5000/v2/users/{0}/days"

        users_with_hashed_passwords = map(lambda t: (t[0], hash_pwd(t[1])),
                                          cls.users)
        populate_db(DBFILE, users_with_hashed_passwords)

    def tearDown(self):
        clear_db(DBFILE)

    def test_bad_auth(self):
        # Qui si testa se un user cerca di modificare i dati relativi a un
        # altro utente
        for auth_user, pwd in self.users:

    def test_bad_auth(self):
        # Qui si testa se un user cerca di modificare i dati relativi a un
        # altro utente
        for auth_user, pwd in self.users:
            for target_user, _ in self.users:
                if auth_user != target_user:
                    url = self.url.format(target_user)
                    resp = requests.post(
                        url, json={"steps":100}, auth=(auth_user, pwd))
                    self.assertEqual(resp.status_code, 401)

        # Qui si testa se un user cerca di modificare i dati relativi a sè
        # sesso, ma lo user non esiste
        wrong_user = ("nouser", "nopwd")
        url_wrong_user = self.url.format(wrong_user[0])
        resp = requests.post(
            url_wrong_user, json={"steps":100}, auth=wrong_user)
        self.assertEqual(resp.status_code, 401)

    def test_not_found(self):
        for user, pwd in self.users:
            url = self.url.format(user) + "/1900-01-01"
            resp = requests.get(url, auth=(user, pwd))
            self.assertEqual(resp.status_code, 404)

    def test_post(self):
        for user, pwd in self.users:
            url = self.url.format(user)

            resp = requests.post(url, json={"steps":100}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)

            resp = requests.post(url, json={"steps":100}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 400)

    def test_get(self):
        for user, pwd in self.users:
            url = self.url.format(user)
            resp = requests.post(
                url, json={"steps":77}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)

            get_uri = resp.json()["uri"]
            resp = requests.get(get_uri, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)

    def test_put(self):
        for user, pwd in self.users:
            url = self.url.format(user)
            resp = requests.post(
                url, json={"steps":11}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(resp.json()["day"]["steps"], 11)

            resp = requests.put(
                url, json={"steps":"22"}, auth=(user, pwd))
            self.assertEqual(resp.status_code, 200)

    def test_delete(self):
        for user, pwd in self.users:
            url = self.url.format(user)
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
