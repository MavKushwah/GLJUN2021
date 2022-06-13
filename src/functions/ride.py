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

from core import DatabaseDriver
from .utils import *


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
    mqtt_client = get_mqtt_client()
    try:
        mqtt_client.connect()
        ride_status: str = ride.get('status')
        if action == 'start' and ride_status == 'ASSIGNED':
            if not db_driver.update_taxi_record(taxi_id=taxi_id,
                                                patch={'updated_on': int(time.time()), 'taxi_on_duty': True}):
                return server_error()
            if db_driver.update_ride(ride_id=ride_id, query={}, update_by={'status': 'RUNNING', 'updated_on': int(time.time())}):
                mqtt_client.send_message(ride.get('topic'), 'your ride has started')
                return ok_request()

        if action == 'end' and ride_status == 'RUNNING':
            if db_driver.update_ride(ride_id=ride_id, query={}, update_by={'status': 'COMPLETED', 'completed_on': int(time.time())}):
                mqtt_client.send_message(ride.get('topic'), 'your ride has ended')
                mqtt_client.send_to_topic(ride.get('topic'), {"completed": True, "ride_id": ride_id})
                if not db_driver.update_taxi_record(taxi_id=taxi_id,
                                                    patch={'updated_on': int(time.time()), 'taxi_on_duty': False}):
                    return server_error()
                return ok_request()
        return bad_request()
    finally:
        mqtt_client.close()
