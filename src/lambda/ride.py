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

from utils import *


def handler(event, context):
    # Get Taxi Id
    taxi_id = get_taxi_id(event)
    # create database helper
    db_driver: DatabaseDriver = get_db_driver()
    existing_taxi = db_driver.get_taxi(taxi_id=taxi_id)
    # if no taxi found, return 401
    if not existing_taxi:
        return unauthorized()
    # validate jwt
    if not validate_token(event, identity=taxi_id, secret=existing_taxi['secret']):
        return unauthorized()
    # extract body for location
    body: dict = get_request_body_json(event)
    # find action
    action: str = body.get('action')
    # find the ride id
    ride_id: str = body.get('ride_id')
    # make sure that the ride is assigned to same taxi
    ride: dict = db_driver.get_ride(ride_id=ride_id)
    # make sure that the ride is assigned to same taxi id
    ride_taxi_id: str = ride.get('taxi_id')
    if ride_taxi_id != taxi_id:
        return bad_request()
    ride_status: str = ride.get('status')
    if action == 'start' and ride_status == 'ASSIGNED':
        if db_driver.patch_ride(ride_id=ride_id, patch={'status': 'RUNNING', 'updated_on': int(time.time())}):
            return ok_request()
    if action == 'end' and ride_status == 'RUNNING':
        if db_driver.patch_ride(ride_id=ride_id, patch={'status': 'COMPLETED', 'completed_on': int(time.time())}):
            return ok_request()
    return bad_request()
