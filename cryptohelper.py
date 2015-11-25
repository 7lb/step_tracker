#! /usr/bin/env python
#-*- coding: utf-8 -*-

"""
Modulo helper che fonisce alcune funzionalità crittografiche di base
"""

from base64 import b64encode, b64decode
import hashlib
from os import urandom

HASH_ALGO = "sha512"
SALT_BYTES = 32
NUM_ROUNDS = 2**18

# Non abbiamo pbkdf2 su python < 2.7.8, quindi la simuliamo
def multihash(hashname, password, salt, rounds):
    """
    Simula pbkdf2
    """
    hashfunc = getattr(hashlib, hashname, None)
    if not hashfunc:
        raise RuntimeError("Wrong hash function name")

    digest = hashfunc(salt + password).digest()

    for _ in xrange(rounds - 1):
        digest = hashfunc(digest).digest()

    return digest


def gensalt(salt_size=SALT_BYTES):
    """
    Genera un salt della dimensione specificata
    """
    return urandom(salt_size)


def hash_pwd(password, salt=None, hashname=HASH_ALGO, rounds=NUM_ROUNDS):
    """
    Esegue l'hashing della password e produce una stringa in base64 adatta
    a essere salvata su un database.

    Nota: il salt è salvato nella stringa in base64
    """
    if not salt:
        salt = gensalt()
    return b64encode(salt + multihash(hashname, password, salt, rounds))


def get_salt(b64str, salt_size=SALT_BYTES):
    """
    Ritorna il salt salvato all'interno della stringa in base64
    """
    return b64decode(b64str)[:salt_size]


def check_pwd(password, b64str, salt_size=SALT_BYTES,
        hashname=HASH_ALGO, rounds=NUM_ROUNDS):
    """
    Controlla se la password fornita e quella criptata combaciano
    """
    return hash_pwd(password, get_salt(b64str, salt_size),
            hashname, rounds) == b64str

