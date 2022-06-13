#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Anirudh Kushwah
# @since 2022.05
#
import base64
import json
import os
import socket
from typing import Optional

from core import DatabaseDriver, JwtHelper, MqttClient

# Global Database Drive
_db_driver: DatabaseDriver = None


def respond(code: Optional[int], body=None, headers=None):
    """ Utility method to generate json response for a lambda call"""
    heads = {
        'Content-Type': 'application/json',
    }
    if heads is not None:
        heads.update(headers)
    return {
        'statusCode': str(code),
        'body': json.dumps(body),
        'headers': heads,
    }


def get_request_body_json(event):
    """ Reads boady from API Gw Event."""
    if event['isBase64Encoded']:
        return json.loads(base64.b64decode(event['body']))
    else:
        return json.loads(event['body'])


def get_taxi_id(event):
    """ Reads taxi id from request headers."""
    return event['headers']['X-Taxi-Id']


def get_user_id(event):
    """ Reads taxi id from request headers."""
    return event['headers']['X-User-Id']


def get_token(event):
    """ Reads security token from request headers."""
    return event['headers']['X-Token']


def validate_token(event, identity: str, secret: str) -> bool:
    """ validates if a request originated from a certain taxi."""
    token = get_token(event)
    return JwtHelper(secret=secret).validate_jwt(identity=identity, token=token)


def get_namespace() -> str:
    return os.environ['NAMESPACE']


def get_mqtt_private_host() -> str:
    return os.environ['MQTT_PRIVATE_IP']


def get_mqtt_public_host() -> str:
    return os.environ['MQTT_PUBLIC_IP']


def get_mongo_uri() -> str:
    if os.environ.get('mode') == 'LOCAL':
        return os.environ['MONGO_URI']
    if os.environ.get('mode') == 'IN_MEMORY':
        return ''
    return os.environ.get("MONGO_URI")


def get_database_name() -> str:
    return '{}-taxi_service'.format(get_namespace()).lower()


def is_connected(hostname, port):
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, port), 2)
    s.close()


def get_mqtt_client() -> MqttClient:
    return MqttClient(host=get_mqtt_private_host(), name='lambda')


def get_db_driver() -> DatabaseDriver:
    global _db_driver
    if _db_driver is None:
        # get mongo uri
        mongo_uri = get_mongo_uri()
        print(f"Mongo uri : {mongo_uri}")
        # create database helper
        _db_driver = DatabaseDriver(mongo_uri=mongo_uri, database_name=get_database_name())
    return _db_driver


def is_valid_location(latitude, longitude) -> bool:
    if not isinstance(latitude, (float, int)) or not isinstance(longitude, (float, int)):
        return False
    if latitude > 180.0 or latitude < -180.0:
        return False
    if longitude > 90.0 or longitude < -90.0:
        return False
    return True


def unauthorized(msg: str = "unauthorized") -> dict:
    return respond(401, {"msg": msg}, {})


def bad_request(msg="bad request") -> dict:
    return respond(400, {"msg": msg}, {})


def ok_request(msg="ok") -> dict:
    return respond(200, {"msg": msg}, {})


def ok_response(body: dict) -> dict:
    return respond(200, body, {})


def server_error(msg="server error") -> dict:
    return respond(500, {"msg": msg}, {})


def taxi_types() -> set:
    return {'MINI', 'ECONOMY', 'SEDAN', 'LUXURY', 'ROYAL'}
