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
    # extract body for location
    body: dict = get_request_body_json(event)
    # find co-ordinates
    location: list = body.get('location')
    if not isinstance(location, list) or len(location) != 2:
        return bad_request()
    # make sure we have correct longitude and latitude
    if not is_valid_location(location[0], location[1]):
        return bad_request()
    # patch location co-ordinates for taxi
    print(f"location update request from taxi {taxi_id} with location {location}")
    taxi_location_detail : dict = {
                "updated_timestamp": time.time(),
                 "location":  {"type": "Point", "coordinates": location},
                "taxi_on_duty": existing_taxi["taxi_on_duty"],
                "active_taxi": existing_taxi["active_taxi"],
                "rider_id": "" # Need to be worked on
    }
    patch_succeeded = db_driver.update_latest_taxi_location(taxi_id=taxi_id, patch=taxi_location_detail)
    if not patch_succeeded:
        return server_error()
    return ok_request()
