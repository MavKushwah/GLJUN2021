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
import uuid

from .utils import *


def handler(event, context):
    # read body
    body: dict = get_request_body_json(event)
    # Handle based on types
    registration_type: str = body.get('type')
    # different validation for taxi and user
    if registration_type == 'taxi':
        return handle_taxi_registration(data=body)
    elif registration_type == 'user':
        return handle_user_registration(data=body)
    else:
        return bad_request()


def handle_taxi_registration(data: dict):
    db_driver: DatabaseDriver = get_db_driver()
    taxi: dict = dict()

    # Validate Taxi Type
    taxi_type: str = data.get('taxi_type')
    if taxi_type not in taxi_types():
        return bad_request()
    taxi['type'] = taxi_type

    # Validate Name
    driver_name = data.get('name')
    if not driver_name:
        return bad_request()
    taxi['name'] = driver_name

    # Validate license
    taxi_license: str = data.get('license')
    if not taxi_license:
        return bad_request()
    taxi['license'] = taxi_license

    # Generate a secret
    random_secret = str(uuid.uuid4())
    taxi['secret'] = random_secret

    # Save
    taxi_id: str = db_driver.create_taxi_record(taxi=taxi)
    return respond(200, {
        "taxi_id": taxi_id, "secret": random_secret
    }, {})


def handle_user_registration(data: dict):
    db_driver: DatabaseDriver = get_db_driver()
    user: dict = dict()

    # Validate Name
    user_name = data.get('name')
    if not user_name:
        return bad_request()
    user['name'] = user_name

    # Generate a secret
    random_secret = str(uuid.uuid4())
    user['secret'] = random_secret

    # Save
    user_id: str = db_driver.create_user_record(user=user)
    return respond(200, {
        "user_id": user_id, "secret": random_secret
    }, {})

