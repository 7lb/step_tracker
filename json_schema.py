#! /usr/bin/env python
#-*- coding: utf-8 -*-

import jsonschema

SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Payload ricevuto in input da richieste POST e PUT",
    "type": "object",
    "properties": {
        "steps": {
            "description": "Numero di passi effettuati in un giorno",
            "type": "integer",
            "minimum": 0
        }
    },
    "additionalProperties": False,
    "required": ["steps"]
}

VALIDATOR = jsonschema.Draft4Validator(SCHEMA)
