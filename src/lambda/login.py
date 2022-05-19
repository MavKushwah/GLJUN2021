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

from database_driver import DatabaseDriver
from mqtthelper import MqttClient
from utils import *


def handler(event, context):
    if not validate_taxi_id(event):
        respond(401, "unauthorized", {})
    # Get Taxi Id
    taxi_id = get_taxi_id(event)
    # create database helper
    db_driver: DatabaseDriver = get_db_driver()
    existing_taxi = db_driver.get_taxi(taxi_id=taxi_id)
    # if no taxi found, return 401
    if not existing_taxi:
        return respond(401, "unauthorized", {})

    # create uuid for the taxi to subscribe to
    taxi_uuid = str(uuid.uuid4())
    # patch
    if not db_driver.update_taxi_record(taxi_id=taxi_id, patch={"uuid": taxi_uuid}):
        return respond(500, "", {})
    # publish a message to this uuid
    mqtt_client: MqttClient = get_mqtt_client()
    # Respond with taxi uuid
    print(f"login request from taxi {taxi_id} was set to uuid {taxi_uuid}")
    mqtt_client.send_to_taxi(taxi_uuid=taxi_uuid, message={"msg": "welcome"})
    return respond(200,
                   {
                       "host": get_mqtt_public_host(),
                       "taxi_uuid": taxi_uuid
                   }, {
                       "X-Taxi-Id": taxi_id
                   })
