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

from utils import *


def handler(event, context):
    # Get Taxi Id
    taxi_id = get_taxi_id(event)
    # create database helper
    db_driver: DatabaseDriver = get_db_driver()
    existing_taxi = db_driver.get_taxi(taxi_id=taxi_id)
    # if no taxi found, return 401
    if not existing_taxi:
        return respond(401, "unauthorized", {})
    # validate jwt
    if not validate_token(event, identity=taxi_id, secret=existing_taxi['secret']):
        respond(401, "unauthorized", {})
    # extract body for location
    body: dict = get_request_body_json(event)
    # find co-ordinates
    location: list = body.get('location')
    if not isinstance(location, list) or len(location) != 2:
        return respond(400, "invalid location", {})
    # make sure we have correct longitude and latitude
    if not is_valid_location(location[0], location[1]):
        return respond(400, "invalid location", {})
    # patch location co-ordinates for taxi
    if not db_driver.update_taxi_record(taxi_id=taxi_id, patch={"location": location}):
        return respond(500, "", {})
    print(f"location update request from taxi {taxi_id} with location {location}")
    return respond(200, "", {"X-Taxi-Id": taxi_id})
