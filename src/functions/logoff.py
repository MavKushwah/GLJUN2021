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

from core import DatabaseDriver, MqttClient
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
    existing_taxi_topic = existing_taxi.get('topic')
    # if no uuid, assume logged off already
    if not existing_taxi_topic:
        return bad_request()
    # update
    if not db_driver.update_taxi_record(taxi_id=taxi_id, patch={
        "logoff_time": int(time.time()),
        "status": "OFFLINE"
    }):
        return server_error()
    # publish a message to this uuid
    mqtt_client: MqttClient = get_mqtt_client()
    # Respond with taxi uuid
    print(f"logoff request from taxi {taxi_id} was reset from topic {existing_taxi_topic}")
    mqtt_client.send_to_topic(topic=existing_taxi_topic, message={"msg": "goodbye"})
    return respond(200,
                   {
                       "host": get_mqtt_public_host(),
                       "topic": existing_taxi_topic
                   }, {
                       "X-Taxi-Id": taxi_id
                   })
