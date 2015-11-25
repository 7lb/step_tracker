#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring, too-many-public-methods

import cryptohelper
import unittest

class CryptoTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = "test"
        cls.salt = "12345678901234567890123456789012"
        cls.rounds = 1  # I test devono essere veloci
        cls.b64str = cryptohelper.hash_pwd(cls.password, cls.salt,
                rounds=cls.rounds)

    def test_get_salt(self):
        self.assertEqual(self.salt, cryptohelper.get_salt(self.b64str))

    def test_check_pwd(self):
        self.assertTrue(cryptohelper.check_pwd(self.password, self.b64str,
            rounds=self.rounds))

if __name__ == "__main__":
    unittest.main()
