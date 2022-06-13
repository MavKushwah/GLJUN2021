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
    # Get User Id
    user_id = get_user_id(event)
    # create database helper
    db_driver: DatabaseDriver = get_db_driver()
    existing_user = db_driver.get_user(user_id=user_id)
    # if no user found, return 401
    if not existing_user:
        return unauthorized()
    # validate jwt
    if not validate_token(event, identity=user_id, secret=existing_user['secret']):
        return unauthorized()
    # get body
    body: dict = get_request_body_json(event)
    # get ride id!
    ride_id: str = body.get('ride_id')
    ride: dict = db_driver.get_ride(ride_id=ride_id)
    if not ride:
        return bad_request()
    if ride.get('user_id') != user_id:
        return bad_request()
    if ride.get('status') != 'REQUESTED':
        return bad_request()
    # get co-ordinates
    location = ride.get('location')
    # Find the nearest taxi(s), and notify them all!
    taxi_list: list = db_driver.find_nearby_taxi(location=location, type=ride.get("type"), radius=50000, limit=2)

    # Create a new Record in Db representing a request from user!
    ride_topic = ride.get('topic')
    # create mqtt client
    mqtt_client = get_mqtt_client()
    try:
        mqtt_client.connect()
        mqtt_client.send_message(ride_topic, 'found {} nearby available taxi(s)', len(taxi_list))
        # send failed!
        if not taxi_list:
            mqtt_client.send_to_topic(ride_topic, {"completed": True})
            return ok_response({"msg": "no nearby taxi", 'success': False})

        for taxi in taxi_list:
            mqtt_client.send_message(ride_topic, 'sending a ride request to taxi {}', taxi.get("name"))
            mqtt_client.send_to_topic(topic=taxi.get('topic'), message={"type": "ride_request", "ride_id": ride_id})
        # say we are waiting
        mqtt_client.send_message(ride_topic, 'waiting for first acceptance by taxi', len(taxi_list))
        expiry = int(time.time()) + 25
        while int(time.time()) < expiry:
            ride = db_driver.get_ride(ride_id=ride_id)
            if ride.get('status') != 'REQUESTED':
                return ok_response({'success': True, 'taxi_id': ride.get('taxi_id')})
            time.sleep(1)
            mqtt_client.send_message(ride_topic, 'waiting for first acceptance by taxi: remaining_time={}',
                                     (expiry - int(time.time())))
        # lets update the record if not assigned!
        if db_driver.update_ride(ride_id=ride_id, query={'status': 'REQUESTED'}, update_by={'status': 'FAILED'}):
            mqtt_client.send_message(ride_topic, 'changed status to failed state')
            mqtt_client.send_to_topic(ride_topic, {"completed": True})
            return ok_response({'success': False, 'msg': 'could not allocate taxi'})
        # something changed
        ride: dict = db_driver.get_ride(ride_id=ride_id)
        if ride.get('status') != 'ASSIGNED':
            return server_error()
        return ok_response({'success': True, 'taxi_id': ride.get('taxi_id')})
    finally:
        mqtt_client.close()
