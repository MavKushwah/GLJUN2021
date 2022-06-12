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

from .utils import *
from core import DatabaseDriver


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
    # are you already occupied
    if existing_taxi['status'] != 'ONLINE':
        return bad_request()
    # extract body for location
    body: dict = get_request_body_json(event)
    # find ride id
    ride_id: str = body.get('ride_id')
    # get ride record
    ride: dict = db_driver.get_ride(ride_id=ride_id)
    if not ride:
        return bad_request()
    # Check state
    mqtt_client = get_mqtt_client()
    try:
        mqtt_client.connect()
        if ride.get('status') != 'REQUESTED':
            mqtt_client.send_message(ride.get('topic'), 'taxi {} had accepted your request', taxi_id)
            return ok_response({"success": False})
        # if not accepted, send a response to user
        accepted: bool = body.get('accepted')
        if not accepted:
            mqtt_client.send_message(ride.get('topic'), 'taxi {} rejected your request', taxi_id)
            return ok_response({"success": True})
        # send taxi response
        mqtt_client.send_message(ride.get('topic'), 'taxi {} accepted your request', taxi_id)
        # run a update
        count: int = db_driver.update_ride(ride_id=ride_id,
                                           query={
                                               'status': 'REQUESTED'
                                           },
                                           update_by={
                                               'updated_on': int(time.time()),
                                               'taxi_id': taxi_id,
                                               'status': 'ASSIGNED'})
        if count == 1:
            # run update
            db_driver.update_taxi_record(taxi_id=taxi_id, patch={'updated_on': int(time.time()), 'status': 'ASSIGNED'})
            # send acceptance
            mqtt_client.send_message(ride.get('topic'), 'taxi {} assigned to your request', taxi_id)
            return ok_response({"success": True})
        return ok_response({"success": False})
    finally:
        mqtt_client.close()
