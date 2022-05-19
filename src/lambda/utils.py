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
import os
from typing import Optional

import base64
import json
import socket

import boto3


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


def get_token(event):
    """ Reads security token from request headers."""
    return event['headers']['X-Token']


def validate_taxi_id(event) -> bool:
    """ validates if a request originated from a certain taxi."""
    taxi_id = get_taxi_id(event)
    token = get_token(event)
    return taxi_id == token


def get_namespace() -> str:
    return os.environ['NAMESPACE']


def get_mqtt_private_host() -> str:
    return os.environ['MQTT_PRIVATE_IP']


def get_mqtt_public_host() -> str:
    return os.environ['MQTT_PUBLIC_IP']


def is_connected(hostname, port):
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, port), 2)
    s.close()
