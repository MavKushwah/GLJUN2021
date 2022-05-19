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
    existing_taxi_uuid = existing_taxi.get('uuid')
    # if no uuid, assume logged off already
    if not existing_taxi_uuid:
        return respond(400, "already logged off", {})
    # update
    if not db_driver.update_taxi_record(taxi_id=taxi_id, patch={"uuid": ""}):
        return respond(500, "", {})
    # publish a message to this uuid
    mqtt_client: MqttClient = get_mqtt_client()
    # Respond with taxi uuid
    print(f"logoff request from taxi {taxi_id} was reset from uuid {existing_taxi_uuid}")
    mqtt_client.send_to_taxi(taxi_uuid=existing_taxi_uuid, message={"msg": "goodbye"})
    return respond(200,
                   {
                       "host": get_mqtt_public_host(),
                       "taxi_uuid": existing_taxi_uuid
                   }, {
                       "X-Taxi-Id": taxi_id
                   })
