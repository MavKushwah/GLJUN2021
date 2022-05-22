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
from database_driver import COL_TAXI


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
    # find co-ordinates
    location: list = body.get('location')
    if not isinstance(location, list) or len(location) != 2:
        return bad_request()
    # make sure we have correct longitude and latitude
    if not is_valid_location(location[0], location[1]):
        return bad_request()

    # Find the nearest taxi(s), and notify them all!
    taxi_list: list = db_driver.run_query(col_name=COL_TAXI, query={
        'status': 'ONLINE',
        'location': {
            '$nearSphere': {
                '$geometry': {
                    'type': "Point",
                    'coordinates': location
                },
                '$maxDistance': 5000}}}, limit=10)
    # send failed!
    if not taxi_list:
        return respond(200, {"msg": "no nearby taxi"}, {})

    # Create a new Record in Db representing a request from user!
    ride_id: str = db_driver.create_ride_record(ride={
        'user_id': user_id,
        'created_on': int(time.time()),
        'status': 'REQUESTED'})
    # @TODO wait for 3 minutes and wait for a assigned status, else fail!
    # Wait till the taxi accepts the ride
    return respond(200, {"ride_id": ride_id}, {})
