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
import uuid

from bson import ObjectId

from .utils import *
from core import DatabaseDriver, MqttClient


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

    topic = f'{get_namespace()}/taxi/{taxi_id}'
    # patch
    if not db_driver.update_taxi_record(taxi_id=taxi_id, patch={
        "topic": topic,
        "login_time": int(time.time()),
        "active_taxi": True
    }):
        return respond(500, "", {})
    # publish a message to this uuid
    mqtt_client: MqttClient = get_mqtt_client()
    # Respond with taxi_id
    print(f"login request from taxi {taxi_id} was set to topic : {topic}")
    mqtt_client.connect()
    mqtt_client.send_to_topic(topic=topic, message={"msg": "welcome"})
    mqtt_client.client.disconnect()
    return respond(200,
                   {
                       "host": get_mqtt_public_host(),
                       "topic": topic
                   }, {
                       "X-Taxi-Id": taxi_id
                   })
