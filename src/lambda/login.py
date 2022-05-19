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

from mqtthelper import MqttClient
from utils import *


def handler(event, context):
    if not validate_taxi_id(event):
        respond(401, "unauthorized", {})
    # Get Taxi Id
    taxi_id = get_taxi_id(event)
    # Get mqtt host
    mqtt_host = get_mqtt_private_host()
    # create uuid for the taxi to subscribe to
    taxi_uuid = str(uuid.uuid4())
    # @TODO store the uuid in mongo db so that future requests can be sent on this uuid
    # publish a message to this uuid
    mqtt_client = MqttClient(host=mqtt_host)
    mqtt_client.connect()
    mqtt_client.send_to_taxi(taxi_uuid=taxi_uuid, message={"taxi_id": taxi_id})
    # Respond with taxi uuid
    print(f"login request from taxi {taxi_id} was set to uuid {taxi_uuid}")
    return respond(200,
                   {
                       "host": get_mqtt_public_host(),
                       "taxi_uuid": taxi_uuid
                   }, {
                       "X-Taxi-Id": taxi_id
                   })


def create_sns_topic(taxi_id) -> str:
    """ Creates a SNS Topic for taxi communication."""

    topic_name = '{}-{}'.format(topic_arn_prefix(), taxi_id)
    print(f"creating sns topic {topic_name} for taxi")
    sns_client = boto3.client('sns')
    response = sns_client.create_topic(Name=topic_name)
    return response['TopicArn']


def topic_arn_prefix() -> str:
    """ Reads the ARN Prefix from Environment."""
    return os.environ['TOPIC_ARN_PREFIX']
