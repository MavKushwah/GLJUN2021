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
from database_driver import COL_RIDES


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
    # find ride id
    ride_id: str = body.get('ride_id')
    # run a update
    count: int = db_driver.patch_by_query(col_name=COL_RIDES,
                                          query={
                                              '_id': ride_id,
                                              'status': 'REQUESTED'
                                          },
                                          patch={
                                              'updated_on': int(time.time()),
                                              'taxi_id': taxi_id,
                                              'status': 'ASSIGNED'})
    if count == 1:
        return ok_request()
    return bad_request()
