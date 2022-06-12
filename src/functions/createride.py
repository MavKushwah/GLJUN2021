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
import time
import uuid

from .utils import *
from core import DatabaseDriver


def handler(event, context):
    # Get User Id
    user_id = get_user_id(event)
    # create database helper
    db_driver: DatabaseDriver = get_db_driver()
    existing_user = db_driver.get_user(user_id=user_id)
    # if no user found, return 401
    if not existing_user:
        return unauthorized("user")
    # validate jwt
    if not validate_token(event, identity=user_id, secret=existing_user['secret']):
        return unauthorized("token invalid")
    # get body
    body: dict = get_request_body_json(event)
    # find co-ordinates
    location: list = body.get('location')
    if not isinstance(location, list) or len(location) != 2:
        return bad_request()
    # make sure we have correct longitude and latitude
    if not is_valid_location(location[0], location[1]):
        return bad_request()

    taxi_type: str = body.get('type')
    # Create a new Record in Db representing a request from user!
    ride_topic = f'{get_namespace()}/ride/{str(uuid.uuid4())}'
    ride_id: str = db_driver.create_new_ride(ride={
        'user_id': user_id,
        'created_on': int(time.time()),
        'topic': ride_topic,
        'status': 'REQUESTED',
        'location': {"type": "Point", "coordinates": location},
        "type": taxi_type
    })
    return ok_response({"ride_id": str(ride_id), "topic": ride_topic, "host": get_mqtt_public_host()})
